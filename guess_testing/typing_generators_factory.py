import collections.abc
import inspect
import typing
from dataclasses import dataclass, field
from functools import partial
from inspect import signature

from guess_testing._base_generator import Generator
from guess_testing.generators import AnyGenerator, BoolGenerator, BytesGenerator, ComplexGenerator, DictGenerator, \
    FloatGenerator, IntGenerator, IterableGenerator, ListGenerator, LiteralGenerator, NoneGenerator, \
    OptionalGenerator, RangeGenerator, SetGenerator, StringGenerator, TupleEllipsisGenerator, TupleGenerator, \
    UnionGenerator


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
        type(None): partial(NoneGenerator),

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
        tuple: TupleGenerator,
        typing.Tuple: TupleGenerator,
        object: AnyGenerator,
        typing.Any: AnyGenerator,
        typing.Optional: OptionalGenerator,
        typing.Union: UnionGenerator,
        typing.Literal: LiteralGenerator
    }

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
            origin, args = annotation.__origin__, annotation.__args__
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
                    if len(args) == 2 and args[1] is type(None):
                        matching_generator = OptionalGenerator
                        args = args[:1]

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
