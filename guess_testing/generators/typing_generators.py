from __future__ import annotations

import random
import re
from functools import partial
from typing import Any, Callable, Optional, Sequence, Type, Union, cast, Literal, Iterable

from guess_testing.generators.final_concrete_generators import BoolGenerator, \
    IntGenerator, FloatGenerator, ComplexGenerator, RangeGenerator, StringGenerator, BytesGenerator, ByteArrayGenerator, \
    MemoryViewGenerator, NoneGenerator, NoneType
from guess_testing.generators.concrete_generators import ListGenerator, DictGenerator, SetGenerator, FrozenSetGenerator, \
    TupleGenerator, TupleEllipsisGenerator, IterableGenerator, handle_qualifiers_by_typing
from guess_testing.generators._base_generator import Generator, GeneratorConfig, RequiresSpecification, \
    TypeSpecification


class LiteralGenerator(Generator[object]):
    """
    Generator for literal values.
    """

    config = GeneratorConfig(-1, False, True)

    __slots__ = ('_literal_values',)

    def __init__(self, literal_values: Sequence[object]):
        """
        Constructor.

        Args:
            literal_values: The literal values to generate.
        """
        self._literal_values = literal_values

    @staticmethod
    def from_generators(sub_generators: Iterable[Generator]) -> LiteralGenerator:
        return LiteralGenerator([sub_generator() for sub_generator in sub_generators])

    @classmethod
    def handle_specification(cls, specification: type, /) -> Optional[RequiresSpecification]:
        if not TypeSpecification.is_any(specification) and TypeSpecification.get_origin(specification) != Literal:
            return None

        args = TypeSpecification.get_args(specification)
        if not args:
            return RequiresSpecification(((-1, TypeSpecification(
                object,
                qualifiers=TypeSpecification.get_qualifiers(specification),
                disqualifiers=TypeSpecification.get_disqualifiers(specification))),), cls.from_generators, ((), {}))

        if TypeSpecification.get_qualifiers(specification):
            return None

        return RequiresSpecification((), cls, ((args,), {}))

    def __call__(self) -> object:
        return random.choice(self._literal_values)

    def __str__(self) -> str:
        literal_values_str = {str(value) if not isinstance(value, str) else f'"{value}"' for value in
                              self._literal_values}
        return f'Literal[{", ".join(sorted(literal_values_str))}]'


class UnionGenerator(Generator[object]):
    """
    Generator for a union of generators.
    """

    config = GeneratorConfig(-1, True, True)

    __slots__ = ('_sub_generators',)

    def __init__(self, *sub_generators: Union[Sequence[Generator], Generator]):
        """
        Constructor.

        Args:
            sub_generators: The generators in the union for generating a value.
        """
        self._sub_generators = []
        for sub_generator in sub_generators:
            if isinstance(sub_generator, list):
                self._sub_generators += sub_generator
            else:
                self._sub_generators.append(sub_generator)

    # todo: generally, typing could also mean `List -> Union[List[str], List[None]]`, but maybe this isn't a very good
    #  idea.
    @classmethod
    def handle_specification(cls, specification: type, /) -> Optional[RequiresSpecification]:
        if TypeSpecification.get_origin(specification) != Union and not TypeSpecification.is_any(specification):
            return None

        args = TypeSpecification.get_args(specification)
        if NoneType in args:
            return None

        qualifiers = handle_qualifiers_by_typing(specification)
        if qualifiers - {'hashable'}:
            return None

        disqualifiers = TypeSpecification.get_disqualifiers(specification).copy()
        if 'union' in disqualifiers:
            return None

        disqualifiers.update({'union', 'optional'})

        if not args:
            # todo: maybe support checking equality of generators and force uniqueness.
            return RequiresSpecification(
                ((partial(random.randint, 2, 16),
                  TypeSpecification(accepted=object, qualifiers=qualifiers, disqualifiers=disqualifiers)),), cls,
                ((), {}))

        return RequiresSpecification(
            tuple(TypeSpecification(accepted=arg, qualifiers=qualifiers, disqualifiers=disqualifiers) for arg in args),
            cls, ((), {}))

    def __call__(self) -> object:
        return random.choice(self._sub_generators)()

    def __str__(self) -> str:
        return f'Union[{", ".join(sorted(set(map(str, self._sub_generators))))}]'


class OptionalGenerator(Generator[Optional[object]]):
    """
    Generator for optional values.
    """

    config = GeneratorConfig(1, True, True)

    __slots__ = '_null_chance', '_sub_generator'

    def __init__(self, sub_generator: Generator, null_chance: float = 0.5):
        """
        Constructor.

        Args:
            sub_generator: The generator to use for generating a value.
            null_chance: The chance of generating a None value, a float between 0 and 1.
        """
        self._null_chance = null_chance
        self._sub_generator = sub_generator

    @classmethod
    def handle_specification(cls, specification: type, /) -> Optional[RequiresSpecification]:
        if TypeSpecification.get_origin(specification) not in (Optional, Union) and not TypeSpecification.is_any(
                specification):
            return None

        args = TypeSpecification.get_args(specification)
        if args and NoneType not in args:
            return None

        if not args:
            args = (object,)

        args = tuple(arg for arg in args if arg != NoneType)
        if len(args) > 1:
            args = (Union[args],)

        qualifiers = handle_qualifiers_by_typing(specification)
        if qualifiers - {'hashable'}:
            return None

        disqualifiers = TypeSpecification.get_disqualifiers(specification).copy()
        if 'optional' in disqualifiers:
            return None

        disqualifiers.update({'none', 'optional'})

        return RequiresSpecification(
            (TypeSpecification(accepted=args[0], qualifiers=qualifiers, disqualifiers=disqualifiers),), cls, ((), {}))

    def __call__(self) -> Optional[object]:
        return None if random.random() < self._null_chance else self._sub_generator()

    def __str__(self) -> str:
        return f'Optional[{self._sub_generator}]'


# todo: add with fixture. maybe not only here.

# All the available generators.
GENERATORS = {
    BoolGenerator,
    IntGenerator,
    FloatGenerator,
    ComplexGenerator,
    StringGenerator,
    BytesGenerator,
    ByteArrayGenerator,
    MemoryViewGenerator,
    RangeGenerator,
    NoneGenerator,
    IterableGenerator,
    ListGenerator,
    TupleEllipsisGenerator,
    FrozenSetGenerator,
    SetGenerator,
    OptionalGenerator,
    DictGenerator,
    TupleGenerator,
    UnionGenerator,
    LiteralGenerator
}


class AnyGenerator(Generator):
    """
    Generator for every possible value.
    """

    generated_type = NoneType
    supported_qualifiers = set()
    config = GeneratorConfig(-1, True, True)

    def __init__(self, sub_generators: Sequence[Generator] = None, max_depth: int = 5, require_hashable: bool = False):
        self._sub_generators = sub_generators
        self._max_depth = max_depth
        self._require_hashable = require_hashable

    @staticmethod
    def generate_generator(given_generator_options: Sequence[Generator] = None, max_depth: int = 5,
                           require_hashable: bool = False) -> Generator:
        """
        Generate a generator by a set of rules.

        Args:
            given_generator_options: The options for a generator to choose from.
            max_depth: The maximum depth for sub generators.
            require_hashable: Does the generator have to be hashable.

        Returns:
            A generator that conforms to the rules.
        """
        generator_options = given_generator_options or GENERATORS
        generator_options = [generator for generator in generator_options if
                             generator.config.requires_only_generators and (
                                     not generator == AnyGenerator and not isinstance(generator, AnyGenerator))]

        if require_hashable:
            generator_options = [generator for generator in generator_options if generator.config.immutable]

        if max_depth <= 1:
            generator_options = [generator for generator in generator_options if
                                 generator.config.sub_generators_number == 0]

        if len(generator_options) == 0:
            raise ValueError('No matching generator found.')

        chosen_generator = random.choice(generator_options)

        if chosen_generator in (SetGenerator, FrozenSetGenerator):
            return cast(Type[Union[SetGenerator, FrozenSetGenerator]], chosen_generator)(
                AnyGenerator.generate_generator(given_generator_options, max_depth - 1, True))

        if chosen_generator == DictGenerator:
            return cast(Type[DictGenerator], chosen_generator)(
                AnyGenerator.generate_generator(given_generator_options, max_depth - 1, True),
                AnyGenerator.generate_generator(given_generator_options, max_depth - 1, require_hashable))

        if chosen_generator.config.sub_generators_number == -1:
            return chosen_generator(
                [AnyGenerator.generate_generator(given_generator_options, max_depth - 1, require_hashable) for _ in
                 range(random.randint(1, 10))])

        return chosen_generator(
            *[AnyGenerator.generate_generator(given_generator_options, max_depth - 1, require_hashable) for _ in
              range(chosen_generator.config.sub_generators_number)])

    def __call__(self) -> Any:
        return self.generate_generator(self._sub_generators, self._max_depth, self._require_hashable)()

    def __str__(self) -> str:
        return 'Any'


GENERATORS.add(AnyGenerator)
