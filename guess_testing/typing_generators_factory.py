import collections.abc
import inspect
import typing
from dataclasses import dataclass, field
from functools import partial
from inspect import signature

from guess_testing.generators._base_generator import Generator
from guess_testing.generators import AnyGenerator, BoolGenerator, BytesGenerator, ComplexGenerator, DictGenerator, \
    FloatGenerator, FrozenSetGenerator, IntGenerator, IterableGenerator, ListGenerator, LiteralGenerator, \
    NoneGenerator, NoneType, OptionalGenerator, RangeGenerator, SetGenerator, StringGenerator, TupleEllipsisGenerator, \
    TupleGenerator, UnionGenerator


@dataclass(frozen=True)
class ParametersGenerators:
    """
    The generators for each type of function parameter.
    """

    positional: typing.Sequence[Generator] = ()
    var_positional: IterableGenerator = \
        field(default_factory=partial(IterableGenerator, NoneGenerator(), min_length=0, max_length=0))
    keyword: typing.Mapping[str, Generator] = field(default_factory=dict)
    var_keyword: DictGenerator = \
        field(default_factory=partial(DictGenerator, NoneGenerator(), NoneGenerator(), min_length=0, max_length=0))


class TypingGeneratorFactory:
    """
    A factory for generating generators from type annotations.
    """

    # Mapping of final typing annotation and the matching generator initialization.
    FINAL_ANNOTATION_TO_GENERATOR = {
        int: partial(IntGenerator),
        float: partial(FloatGenerator),
        complex: partial(ComplexGenerator),
        bool: partial(BoolGenerator),
        str: partial(StringGenerator),
        bytes: partial(BytesGenerator),
        range: partial(RangeGenerator),
        None: partial(NoneGenerator),
        NoneType: partial(NoneGenerator),

        typing.Iterable: lambda: IterableGenerator(AnyGenerator()),
        collections.abc.Iterable: lambda: IterableGenerator(AnyGenerator()),

        list: lambda: ListGenerator(AnyGenerator()),
        typing.List: lambda: ListGenerator(AnyGenerator()),

        dict: lambda: DictGenerator(AnyGenerator(require_hashable=True), AnyGenerator()),
        typing.Dict: lambda: DictGenerator(AnyGenerator(require_hashable=True), AnyGenerator()),
        typing.Mapping: lambda: DictGenerator(AnyGenerator(require_hashable=True), AnyGenerator()),
        collections.abc.Mapping: lambda: DictGenerator(AnyGenerator(require_hashable=True), AnyGenerator()),

        set: lambda: SetGenerator(AnyGenerator(require_hashable=True)),
        typing.Set: lambda: SetGenerator(AnyGenerator(require_hashable=True)),
        collections.abc.Set: lambda: SetGenerator(AnyGenerator(require_hashable=True)),

        frozenset: lambda: FrozenSetGenerator(AnyGenerator(require_hashable=True)),
        typing.FrozenSet: lambda: FrozenSetGenerator(AnyGenerator(require_hashable=True)),

        tuple: lambda: TupleEllipsisGenerator(AnyGenerator()),
        typing.Tuple: lambda: TupleEllipsisGenerator(AnyGenerator()),

        object: partial(AnyGenerator),
        typing.Any: partial(AnyGenerator),

        typing.Optional: lambda: OptionalGenerator(AnyGenerator())
    }

    # Mapping of continuous typing annotation and the matching generator.
    CONTINUOUS_ANNOTATION_TO_GENERATOR = {
        typing.Iterable: IterableGenerator,
        collections.abc.Iterable: IterableGenerator,
        list: ListGenerator,
        typing.List: ListGenerator,
        dict: DictGenerator,
        typing.Dict: DictGenerator,
        typing.Mapping: DictGenerator,
        collections.abc.Mapping: DictGenerator,
        set: SetGenerator,
        typing.Set: SetGenerator,
        collections.abc.Set: SetGenerator,
        frozenset: FrozenSetGenerator,
        typing.FrozenSet: FrozenSetGenerator,
        tuple: TupleGenerator,
        typing.Tuple: TupleGenerator,
        object: AnyGenerator,
        typing.Any: AnyGenerator,
        typing.Optional: OptionalGenerator,
        typing.Union: UnionGenerator,
        typing.Literal: LiteralGenerator
    }

    MAX_SUB_GENERATORS = 10
    MIN_SUB_GENERATORS = 1

    @staticmethod
    def new_get_generator(annotation: type, limit: int = 5) -> Generator:
        import random
        generators_ = Generator.get_inheritances()
        random.shuffle(generators_)

        # todo: maybe shuffle and break on the first match to not have things to the power of options.

        found = None
        for possible_match in generators_:
            requirements = possible_match.handle_specification(annotation)
            if requirements is None or limit == 1 and requirements.to_resolve:
                continue

            resolved = []
            matches = True

            for requirement in requirements.to_resolve:
                if isinstance(requirement, tuple):
                    amount, type_to_resolve = requirement
                    if callable(amount):
                        while not TypingGeneratorFactory.MIN_SUB_GENERATORS <= (
                                generated_amount := amount()) <= TypingGeneratorFactory.MAX_SUB_GENERATORS:
                            pass
                        amount = generated_amount
                    elif amount == -1:
                        amount = random.randint(TypingGeneratorFactory.MIN_SUB_GENERATORS,
                                                TypingGeneratorFactory.MAX_SUB_GENERATORS)
                    packed = True
                else:
                    amount = 1
                    type_to_resolve = requirement
                    packed = False

                matching = [TypingGeneratorFactory.new_get_generator(type_to_resolve, limit - 1) for _ in
                            range(amount)]
                if not all(matching):
                    matches = False
                    break

                if packed:
                    resolved.append(matching)
                else:
                    resolved += matching

            if not matches:
                continue

            found = requirements.callback(*resolved, *requirements.callback_arguments[0],
                                          **requirements.callback_arguments[1])
            break

        return found

    @staticmethod
    def get_generator(annotation: type) -> Generator:
        """
        Get a generator by annotation.

        Args:
            annotation: The type annotation to get a generator for.

        Returns:
            The matching generator.
        """
        if annotation is inspect._empty:
            raise TypeError('Type not specified')

        # todo: maybe support more typing types.
        if annotation in TypingGeneratorFactory.FINAL_ANNOTATION_TO_GENERATOR:
            return TypingGeneratorFactory.FINAL_ANNOTATION_TO_GENERATOR[annotation]()

        if annotation.__module__ == 'typing':
            origin, args = typing.get_origin(annotation), typing.get_args(annotation)
            if origin in TypingGeneratorFactory.CONTINUOUS_ANNOTATION_TO_GENERATOR:
                if not args:
                    return TypingGeneratorFactory.FINAL_ANNOTATION_TO_GENERATOR[annotation]()

                matching_generator = TypingGeneratorFactory.CONTINUOUS_ANNOTATION_TO_GENERATOR[origin]
                args_generators = None

                # Handle Tuple and ellipsis written as Tuple[TYPE, ...].
                if origin is tuple:
                    if args[-1] is Ellipsis:
                        if len(args) != 2:
                            raise ValueError(f'Invalid ellipsis usage in type tuple: "{annotation}".')

                        matching_generator = TupleEllipsisGenerator
                        args = args[:1]

                # Handle Optional written as Union[TYPE, NoneType].
                elif origin is typing.Union:
                    if None in args or NoneType in args:
                        return OptionalGenerator(
                            UnionGenerator([TypingGeneratorFactory.get_generator(arg) for arg in args if
                                            arg not in {None, NoneType}]))

                # Handle Literal written as Literal[VALUE].
                elif origin is typing.Literal:
                    matching_generator = LiteralGenerator
                    args_generators = args

                args_generators = args_generators or [TypingGeneratorFactory.get_generator(arg) for arg in args]
                return matching_generator(args_generators) if \
                    matching_generator.config.sub_generators_number == -1 else \
                    matching_generator(*args_generators)

        raise ValueError(f'Could not interpret type "{annotation}".')

    @staticmethod
    def get_generators(func: typing.Callable) -> ParametersGenerators:
        """
        Get generators for a function by its type annotations.

        Args:
            func: The function to get generators for.

        Returns:
            The generators matching the function's type annotations.
        """
        positional = []
        var_positional = None
        keyword = {}
        var_keyword = None

        for name, param in signature(func).parameters.items():
            if param.kind == inspect._ParameterKind.POSITIONAL_ONLY:
                positional.append(TypingGeneratorFactory.get_generator(param.annotation))
            elif param.kind == inspect._ParameterKind.VAR_POSITIONAL:
                var_positional = TypingGeneratorFactory.get_generator(typing.Iterable[param.annotation])
            elif param.kind in (inspect._ParameterKind.POSITIONAL_OR_KEYWORD, inspect._ParameterKind.KEYWORD_ONLY):
                keyword[name] = TypingGeneratorFactory.get_generator(param.annotation)
            else:
                var_keyword = TypingGeneratorFactory.get_generator(typing.Dict[str, param.annotation])

        return ParametersGenerators(positional=positional,
                                    keyword=keyword,
                                    **dict(var_positional=var_positional) if var_positional else {},
                                    **dict(var_keyword=var_keyword) if var_keyword else {})
