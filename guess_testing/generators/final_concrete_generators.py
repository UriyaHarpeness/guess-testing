import random
import string
from typing import Optional

from guess_testing.generators._base_generator import GeneratorConfig, RequiresSpecification, TypeSpecification
from guess_testing.generators._concrete_generator import handle_qualifiers_by_typing
from guess_testing.generators._final_concrete_generator import FinalConcreteGenerator

NoneType = type(None)  # Appears as part of `types` module at later python versions.


class IntGenerator(FinalConcreteGenerator[int]):
    """
    Generator for integer values.
    """

    generated_type = int
    supported_qualifiers = {'hashable'}
    unsupported_disqualifiers = set()
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


class FloatGenerator(FinalConcreteGenerator[float]):
    """
    Generator for float values.
    """

    generated_type = float
    supported_qualifiers = {'hashable'}
    unsupported_disqualifiers = set()
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
            special_cases_chance: The chance of generating one of float's special cases, a float between 0 and 1.
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


class ComplexGenerator(FinalConcreteGenerator[complex]):
    """
    Generator for complex values.
    """

    generated_type = complex
    supported_qualifiers = {'hashable'}
    unsupported_disqualifiers = set()
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


class BoolGenerator(FinalConcreteGenerator[bool]):
    """
    Generator for boolean values.
    """

    generated_type = bool
    supported_qualifiers = {'hashable'}
    unsupported_disqualifiers = set()
    config = GeneratorConfig(0, True, True)

    __slots__ = ()

    def __call__(self) -> bool:
        return random.choice((True, False))


class StringGenerator(FinalConcreteGenerator[str]):
    """
    Generator for string values.
    """

    generated_type = str
    supported_qualifiers = {'hashable'}
    unsupported_disqualifiers = set()
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


class BytesGenerator(StringGenerator, FinalConcreteGenerator[bytes]):
    """
    Generator for bytes values.
    """

    generated_type = bytes
    supported_qualifiers = {'hashable'}
    unsupported_disqualifiers = set()
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


class ByteArrayGenerator(BytesGenerator, FinalConcreteGenerator[bytearray]):
    """
    Generator for bytearray values.
    """

    generated_type = bytearray
    supported_qualifiers = set()
    unsupported_disqualifiers = set()
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


class MemoryViewGenerator(BytesGenerator, FinalConcreteGenerator[memoryview]):
    """
    Generator for memoryview values.
    """

    generated_type = memoryview
    supported_qualifiers = {'hashable'}
    unsupported_disqualifiers = set()
    config = GeneratorConfig(0, True, True)

    __slots__ = ('_bytearray_chance',)

    def __init__(self, min_length: int = 0, max_length: int = 2 ** 5, selection: str = string.printable,
                 encoding: str = 'utf-8', bytearray_chance: float = 0.5):
        """
        Constructor.

        Args:
            min_length: Minimum length (including).
            max_length: Maximum value (including).
            selection: A string to choose characters from.
            encoding: The encoding to use.
            bytearray_chance: The chance of creating the memoryview over bytearray, a float between 0 and 1.
        """
        super().__init__(min_length, max_length, selection, encoding)
        self._bytearray_chance = bytearray_chance

    @classmethod
    def handle_specification(cls, specification: type, /) -> Optional[RequiresSpecification]:
        if not cls._matches_specification(specification) or TypeSpecification.get_args(specification):
            return None

        if 'hashable' in handle_qualifiers_by_typing(specification):
            return RequiresSpecification((), cls, ((), {'bytearray_chance': 0}))

        return RequiresSpecification((), cls, ((), {}))

    def __call__(self) -> memoryview:
        created = super().__call__()
        return memoryview(bytearray(created) if random.random() < self._bytearray_chance else created)


class NoneGenerator(FinalConcreteGenerator[None]):
    """
    Generator for a None value.
    """

    generated_type = NoneType
    supported_qualifiers = {'hashable'}
    unsupported_disqualifiers = {'none'}
    config = GeneratorConfig(0, True, True)

    __slots__ = ()

    def __init__(self):
        """
        Constructor.
        """

    @classmethod
    def handle_specification(cls, specification: type, /) -> Optional[RequiresSpecification]:
        if (not cls._matches_specification(specification) or TypeSpecification.get_args(
                specification)) and specification is not None:
            return None
        return RequiresSpecification((), cls, ((), {}))

    def __call__(self) -> None:
        return None


class RangeGenerator(FinalConcreteGenerator[range]):
    """
    Generator for ranges.
    """

    generated_type = range
    supported_qualifiers = {'hashable'}
    unsupported_disqualifiers = set()
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
        lower_limit = max(self._min_step, -abs(start - stop))
        upper_limit = min(self._max_step, abs(start - stop))
        step = random.randint(lower_limit, upper_limit - 1)
        if step >= 0:
            step += 1
        start, stop = sorted((start, stop), reverse=step < 0)
        return range(start, stop, step)
