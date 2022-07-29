import random
import string
from typing import Any, Callable, Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple, Type, Union, cast

from guess_testing._base_generator import Generator, GeneratorConfig

NoneType = type(None)


class IntGenerator(Generator[int]):
    """
    Generator for integer values.
    """

    generated_type = int
    config = GeneratorConfig(0, True, True)

    __slots__ = '_start', '_stop', '_step'

    def __init__(self, start: int = -2 ** 16, stop: int = 2 ** 16, step: int = 1):
        """
        Constructor.

        Args:
            start: Minimum value (including).
            stop: Maximum value (excluding).
            step: The jumps between the possible values from the minimum value until the maximum value.
        """
        self._start = start
        self._stop = stop
        self._step = step

    def __call__(self) -> int:
        return random.randrange(self._start, self._stop, self._step)

    def __str__(self) -> str:
        return 'int'


class FloatGenerator(Generator[float]):
    """
    Generator for float values.
    """

    generated_type = float
    config = GeneratorConfig(0, True, True)

    # Float's special cases.
    SPECIAL_CASES = (float('inf'), float('-inf'), float('nan'))

    __slots__ = '_start', '_stop', '_step', '_special_cases_chance'

    def __init__(self, start: float = -2 ** 16, stop: float = 2 ** 16, step: Optional[float] = None,
                 special_cases_chance: float = 1 / 2 ** 8):
        """
        Constructor.

        Args:
            start: Minimum value (including).
            stop: Maximum value (excluding).
            step: The jumps between the possible values from the minimum value until the maximum value.
            special_cases_chance: The change of generating one of float's special cases, a float between 0 and 1.
        """
        self._start = start
        self._stop = stop
        self._step = step
        self._special_cases_chance = special_cases_chance

    def __call__(self) -> float:
        if random.random() < self._special_cases_chance:
            return random.choice(self.SPECIAL_CASES)

        if not self._step:
            return random.uniform(self._start, self._stop)
        return random.randrange(int(self._start / self._step), int(self._stop / self._step)) * self._step

    def __str__(self) -> str:
        return 'float'


class ComplexGenerator(Generator[complex]):
    """
    Generator for complex values.
    """

    generated_type = complex
    config = GeneratorConfig(0, True, True)

    __slots__ = '_real_generator', '_imaginary_generator'

    def __init__(self, real_start: float = -2 ** 16, real_stop: float = 2 ** 16, real_step: Optional[float] = None,
                 real_special_cases_chance: float = 1 / 2 ** 8, imaginary_start: float = -2 ** 16,
                 imaginary_stop: float = 2 ** 16, imaginary_step: Optional[float] = None,
                 imaginary_special_cases_chance: float = 1 / 2 ** 8):
        """
        Constructor.

        Args:
            real_start: Minimum value for the real part (including).
            real_stop: Maximum value for the real part (excluding).
            real_step: The jumps between the possible values from the minimum value until the maximum value for the real
                part.
            imaginary_start: Minimum value for the imaginary part (including).
            imaginary_stop: Maximum value for the imaginary part (excluding).
            imaginary_step: The jumps between the possible values from the minimum value until the maximum value for the
                imaginary part.
        """
        self._real_generator = FloatGenerator(real_start, real_stop, real_step, real_special_cases_chance)
        self._imaginary_generator = FloatGenerator(imaginary_start, imaginary_stop, imaginary_step,
                                                   imaginary_special_cases_chance)

    def __call__(self) -> complex:
        return complex(self._real_generator(), self._imaginary_generator())

    def __str__(self) -> str:
        return 'complex'


class BoolGenerator(Generator[bool]):
    """
    Generator for boolean values.
    """

    generated_type = bool
    config = GeneratorConfig(0, True, True)

    __slots__ = ()

    def __call__(self) -> bool:
        return random.choice((True, False))

    def __str__(self) -> str:
        return 'bool'


class StringGenerator(Generator[str]):
    """
    Generator for string values.
    """

    generated_type = str
    config = GeneratorConfig(0, True, True)

    __slots__ = '_min_length', '_max_length', '_selection'

    def __init__(self, min_length: int = 0, max_length: int = 2 ** 5, selection: str = string.printable):
        """
        Constructor.

        Args:
            min_length: Minimum length (including).
            max_length: Maximum value (including).
            selection: A string to choose characters from.
        """
        self._min_length = min_length
        self._max_length = max_length
        self._selection = selection

    def __call__(self) -> str:
        return ''.join(
            random.choice(self._selection) for _ in range(random.randrange(self._min_length, self._max_length + 1)))

    def __str__(self) -> str:
        return 'str'


class BytesGenerator(StringGenerator, Generator[bytes]):
    """
    Generator for bytes values.
    """

    generated_type = bytes
    config = GeneratorConfig(0, True, True)

    __slots__ = ('_encoding',)

    def __init__(self, min_length: int = 0, max_length: int = 2 ** 5, selection: str = string.printable,
                 encoding: str = 'utf-8'):
        """
        Constructor.

        Args:
            min_length: Minimum length (including).
            max_length: Maximum value (including).
            selection: A string to choose characters from.
            encoding: The encoding to use.
        """
        super().__init__(min_length, max_length, selection)
        self._encoding = encoding

    def __call__(self) -> bytes:
        return super().__call__().encode(self._encoding)

    def __str__(self) -> str:
        return 'bytes'


class ByteArrayGenerator(BytesGenerator, Generator[bytearray]):
    """
    Generator for bytearray values.
    """

    generated_type = bytearray
    config = GeneratorConfig(0, True, False)

    __slots__ = ()

    def __init__(self, min_length: int = 0, max_length: int = 2 ** 5, selection: str = string.printable,
                 encoding: str = 'utf-8'):
        """
        Constructor.

        Args:
            min_length: Minimum length (including).
            max_length: Maximum value (including).
            selection: A string to choose characters from.
            encoding: The encoding to use.
        """
        super().__init__(min_length, max_length, selection, encoding)

    def __call__(self) -> bytearray:
        return bytearray(super().__call__())

    def __str__(self) -> str:
        return 'bytearray'


class MemoryViewGenerator(BytesGenerator, Generator[memoryview]):
    """
    Generator for memoryview values.
    """

    generated_type = memoryview
    config = GeneratorConfig(0, True, True)

    def __init__(self, min_length: int = 0, max_length: int = 2 ** 5, selection: str = string.printable,
                 encoding: str = 'utf-8'):
        """
        Constructor.

        Args:
            min_length: Minimum length (including).
            max_length: Maximum value (including).
            selection: A string to choose characters from.
            encoding: The encoding to use.
        """
        super().__init__(min_length, max_length, selection, encoding)

    def __call__(self) -> memoryview:
        return memoryview(super().__call__())

    def __str__(self) -> str:
        return 'memoryview'


class LiteralGenerator(Generator[object]):
    """
    Generator for a literal value.
    """

    generated_type = NoneType
    config = GeneratorConfig(-1, False, True)

    __slots__ = ('_literal_values',)

    def __init__(self, literal_values: Sequence[object]):
        """
        Constructor.

        Args:
            literal_values: The literal value to generate.
        """
        self._literal_values = literal_values

    def __call__(self) -> object:
        return random.choice(self._literal_values)

    def __str__(self) -> str:
        return f'Literal[{", ".join(sorted(set(map(str, self._literal_values))))}]'


class NoneGenerator(Generator[None]):
    """
    Generator for a None value.
    """

    generated_type = NoneType
    config = GeneratorConfig(0, True, True)

    __slots__ = ()

    def __init__(self):
        """
        Constructor.
        """

    def __call__(self) -> None:
        return None

    def __str__(self) -> str:
        return 'None'


class UnionGenerator(Generator[object]):
    """
    Generator for a union of generators.
    """

    generated_type = NoneType
    config = GeneratorConfig(-1, True, True)

    __slots__ = ('_sub_generators',)

    def __init__(self, sub_generators: Sequence[Generator]):
        """
        Constructor.

        Args:
            sub_generators: The generators in the union for generating a value.
        """
        self._sub_generators = sub_generators

    def __call__(self) -> object:
        return random.choice(self._sub_generators)()

    def __str__(self) -> str:
        return f'Union[{", ".join(sorted(set(map(str, self._sub_generators))))}]'


class IterableGenerator(Generator[Iterable[object]]):
    """
    Generator for iterable values.
    """

    generated_type = NoneType
    config = GeneratorConfig(1, True, False)

    __slots__ = '_sub_generator', '_min_length', '_max_length'

    def __init__(self, sub_generator: Generator, min_length: int = 0, max_length: int = 2 ** 4):
        """
        Constructor.

        Args:
            sub_generator: The generator to use for filling the iterable.
            min_length: Minimum length (including).
            max_length: Maximum length (including).
        """
        self._sub_generator = sub_generator
        self._min_length = min_length
        self._max_length = max_length

    def __call__(self) -> Iterable[object]:
        return (self._sub_generator() for _ in range(random.randint(self._min_length, self._max_length)))

    def __str__(self) -> str:
        return f'Iterable[{self._sub_generator}]'


class ListGenerator(IterableGenerator, Generator[List[object]]):
    """
    Generator for a list of values.
    """

    generated_type = list
    config = GeneratorConfig(1, True, False)

    __slots__ = ()

    def __call__(self) -> List[object]:
        return list(super().__call__())

    def __str__(self) -> str:
        return f'List[{self._sub_generator}]'


class SetGenerator(IterableGenerator, Generator[Set[object]]):
    """
    Generator for a set of values.
    """

    generated_type = set
    config = GeneratorConfig(1, True, False)

    __slots__ = ()

    def __call__(self) -> Set[object]:
        return set(super().__call__())

    def __str__(self) -> str:
        return f'Set[{self._sub_generator}]'


class FrozenSetGenerator(IterableGenerator, Generator[FrozenSet[object]]):
    """
    Generator for a frozenset of values.
    """

    generated_type = frozenset
    config = GeneratorConfig(1, True, True)

    __slots__ = ()

    def __call__(self) -> FrozenSet[object]:
        return frozenset(super().__call__())

    def __str__(self) -> str:
        return f'FrozenSet[{self._sub_generator}]'


class TupleEllipsisGenerator(IterableGenerator, Generator[Tuple[object, ...]]):
    """
    Generator for a tuple of values with ellipsis.
    """

    generated_type = tuple
    config = GeneratorConfig(1, True, True)

    __slots__ = ()

    def __call__(self) -> Tuple[object, ...]:
        return tuple(super().__call__())

    def __str__(self) -> str:
        return f'Tuple[{str(self._sub_generator)}, ...]'


class RangeGenerator(Generator[range]):
    """
    Generator for ranges.
    """

    generated_type = range
    config = GeneratorConfig(0, True, True)

    __slots__ = '_minimum', '_maximum', '_min_step', '_max_step'

    def __init__(self, minimum: int = -2 ** 8, maximum: int = 2 ** 8, min_step: int = -2 ** 4, max_step: int = 2 ** 4):
        """
        Constructor.

        Args:
            minimum: The minimum value for the range (including).
            maximum: The maximum value for the range (including).
            min_step: The minimum step for the range (including).
            max_step: The maximum step for the range (including).
        """
        self._minimum = minimum
        self._maximum = maximum
        self._min_step = min_step
        self._max_step = max_step

    def __call__(self) -> range:
        start = random.randint(self._minimum, self._maximum - 1)
        stop = random.randint(start + 1, self._maximum)
        step = random.choice(
            [x for x in range(self._min_step, self._max_step) if x != 0 and abs(x) <= abs(start - stop)])
        start, stop = sorted((start, stop), reverse=step < 0)
        return range(start, stop, step)

    def __str__(self) -> str:
        return 'range'


class OptionalGenerator(Generator[Optional[object]]):
    """
    Generator for optional values.
    """

    generated_type = NoneType
    config = GeneratorConfig(1, True, True)

    __slots__ = '_null_chance', '_sub_generator'

    def __init__(self, sub_generator: Generator, null_chance: float = 0.5):
        """
        Constructor.

        Args:
            sub_generator: The generator to use for generating a value.
            null_chance: The change of generating a None value, a float between 0 and 1.
        """
        self._null_chance = null_chance
        self._sub_generator = sub_generator

    def __call__(self) -> Optional[object]:
        return None if random.random() < self._null_chance else self._sub_generator()

    def __str__(self) -> str:
        return f'Optional[{self._sub_generator}]'


class DictGenerator(Generator[Dict[object, object]]):
    """
    Generator for a dictionary of values.
    """

    generated_type = dict
    config = GeneratorConfig(2, True, False)

    __slots__ = '_keys_generator', '_values_generator', '_min_length', '_max_length'

    def __init__(self, keys_generator: Generator, values_generator: Generator, min_length: int = 0,
                 max_length: int = 2 ** 4):
        """
        Constructor.

        Args:
            keys_generator: The generator for the keys of the dictionary.
            values_generator: The generator for the values of the dictionary.
            min_length: The minimum length of the dictionary (including).
            max_length: The maximum length of the dictionary (including).
        """
        self._keys_generator = keys_generator
        self._values_generator = values_generator
        self._min_length = min_length
        self._max_length = max_length

    def __call__(self) -> Dict[object, object]:
        return {self._keys_generator(): self._values_generator() for _ in
                range(random.randint(self._min_length, self._max_length))}

    def __str__(self) -> str:
        return f'Dict[{self._keys_generator}, {self._values_generator}]'


class TupleGenerator(Generator[Tuple[object, ...]]):
    """
    Generator for a tuple of values of different types.
    """

    generated_type = tuple
    config = GeneratorConfig(-1, True, True)

    __slots__ = ('_sub_generators',)

    def __init__(self, sub_generators: Sequence[Generator]):
        """
        Constructor.

        Args:
            sub_generators: The generators to use for generating the tuple.
        """
        self._sub_generators = sub_generators

    def __call__(self) -> Tuple[object, ...]:
        return tuple(generator() for generator in self._sub_generators)

    def __str__(self) -> str:
        return f'Tuple[{", ".join(map(str, self._sub_generators))}]'


class TransformGenerator(Generator[object]):
    """
    Generator for running a transformation.
    """

    generated_type = NoneType
    config = GeneratorConfig(1, False, False)

    __slots__ = '_sub_generator', '_transformer'

    def __init__(self, sub_generator: Generator, transformer: Callable[[Any], Any]):
        """
        Constructor.

        Args:
            sub_generator: The generator to use for generating the initial value.
            transformer: The transformation to run on the value received from the generator.
        """
        self._sub_generator = sub_generator
        self._transformer = transformer

    def __call__(self) -> object:
        return self._transformer(self._sub_generator())

    def __str__(self) -> str:
        return f'Transform[{self._sub_generator}, {self._transformer}]'


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
    LiteralGenerator,
    TransformGenerator
}


class AnyGenerator(Generator):
    """
    Generator for every possible value.
    """

    generated_type = NoneType
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
