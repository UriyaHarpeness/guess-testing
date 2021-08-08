import abc
import inspect
import random
import typing
from dataclasses import dataclass
from functools import partial
from inspect import signature
from typing import Any, Callable, Dict
from typing import Generator as GeneratorT
from typing import List, Optional, Sequence, Set, Tuple


@dataclass
class GeneratorConfig:
    """
    Configuration describing each generator.
    """
    sub_generators_number: int  # The number of sub generators the generator requires.
    requires_only_generators: bool  # Does the generator require only generators for initialization.
    immutable: bool  # Is the generator's result immutable.


class Generator(abc.ABC):
    """
    Base class for the generators.
    """

    @property
    @abc.abstractmethod
    def config(self) -> GeneratorConfig:
        """
        Configuration of the generator.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __call__(self) -> Any:
        """
        Generate a value.
        """

    def __str__(self) -> str:
        """
        String representation of the generator.
        """
        return '%s(%r)' % (self.__class__, self.__dict__)

    def __repr__(self) -> str:
        """
        String representation of the generator.
        """
        return str(self)


class IntGenerator(Generator):
    """
    Generator for integer values.
    """

    config = GeneratorConfig(0, True, True)

    def __init__(self, start: int = -2 ** 16, stop: int = 2 ** 16, step: int = 1):
        """
        Constructor.

        Args:
            start: Minimum value (including).
            stop: Maximum value (excluding).
            step: The jumps between the possible values from the minimum value until the maximum value.
        """
        self.start = start
        self.stop = stop
        self.step = step

    def __call__(self) -> int:
        return random.randrange(self.start, self.stop, self.step)


class FloatGenerator(Generator):
    """
    Generator for float values.
    """

    config = GeneratorConfig(0, True, True)

    def __init__(self, start: float = -2 ** 16, stop: float = 2 ** 16, step: Optional[float] = None):
        """
        Constructor.

        Args:
            start: Minimum value (including).
            stop: Maximum value (excluding).
            step: The jumps between the possible values from the minimum value until the maximum value.
        """
        self.start = start
        self.stop = stop
        self.step = step

    def __call__(self) -> float:
        if not self.step:
            return random.uniform(self.start, self.stop)
        return random.randrange(int(self.start / self.step), int(self.stop / self.step)) * self.step


class BoolGenerator(Generator):
    """
    Generator for boolean values.
    """

    config = GeneratorConfig(0, True, True)

    def __call__(self) -> bool:
        return random.choice((True, False))


class StringGenerator(Generator):
    """
    Generator for string values.
    """

    config = GeneratorConfig(0, True, True)

    # A collection of possible character batches to use.
    UPPERCASE = ''.join(chr(x) for x in range(ord('A'), ord('Z') + 1))
    LOWERCASE = ''.join(chr(x) for x in range(ord('a'), ord('z') + 1))
    NUMBERS = ''.join(chr(x) for x in range(ord('0'), ord('9') + 1))
    READABLE_OTHER = '!@#$%^&*()-=_+{}[]\\|/<>\'"`~;.,\n\t '
    ALL = ''.join(chr(x) for x in range(256))
    READABLE = UPPERCASE + LOWERCASE + NUMBERS + READABLE_OTHER

    def __init__(self, min_length: int = 0, max_length: int = 2 ** 5, selection: str = READABLE):
        """
        Constructor.

        Args:
            min_length: Minimum length (including).
            max_length: Maximum value (including).
            selection: A string to choose characters from.
        """
        self.min_length = min_length
        self.max_length = max_length
        self.selection = selection

    def __call__(self) -> str:
        return ''.join(
            random.choice(self.selection) for _ in range(random.randrange(self.min_length, self.max_length + 1)))


class BytesGenerator(StringGenerator):
    """
    Generator for bytes values.
    """

    config = GeneratorConfig(0, True, True)

    def __init__(self, min_length: int = 0, max_length: int = 2 ** 5, selection: str = StringGenerator.READABLE,
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
        self.encoding = encoding

    def __call__(self) -> bytes:
        return super().__call__().encode(self.encoding)


class ChooseGenerator(Generator):
    """
    Generator for choosing a random given value.
    """

    config = GeneratorConfig(-1, False, True)

    def __init__(self, fixed_values: Sequence[Any]):
        """
        Constructor.

        Args:
            fixed_values: The fixed values to choose from for generating a value.
        """
        self.fixed_values = fixed_values

    def __call__(self) -> Any:
        return random.choice(self.fixed_values)


class FixedGenerator(Generator):
    """
    Generator for a fixed value.
    """

    config = GeneratorConfig(1, False, True)

    def __init__(self, fixed_value: Any):
        """
        Constructor.

        Args:
            fixed_value: The fixed value to generate.
        """
        self.fixed_value = fixed_value

    def __call__(self) -> Any:
        return self.fixed_value


class GeneratorCollection(Generator):
    """
    Generator for choosing and calling generators.
    """

    config = GeneratorConfig(-1, True, True)

    def __init__(self, sub_generators: Sequence[Generator]):
        """
        Constructor.

        Args:
            sub_generators: The generators to choose from for generating a value.
        """
        self.sub_generators = sub_generators

    def __call__(self) -> Any:
        return random.choice(self.sub_generators)()


class SequenceGenerator(Generator):
    """
    Generator for a sequence of values.
    """

    config = GeneratorConfig(1, True, False)

    def __init__(self, sub_generator: Generator, min_length: int = 0, max_length: int = 2 ** 4):
        """
        Constructor.

        Args:
            sub_generator: The generator to use for filling the sequence.
            min_length: Minimum length (including).
            max_length: Maximum length (including).
        """
        self.sub_generator = sub_generator
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self) -> GeneratorT[Any, Any, Any]:
        return (self.sub_generator() for _ in range(random.randint(self.min_length, self.max_length)))


class ListGenerator(SequenceGenerator):
    """
    Generator for a list of values.
    """

    config = GeneratorConfig(1, True, False)

    def __call__(self) -> List[Any]:
        return list(super().__call__())


class SetGenerator(SequenceGenerator):
    """
    Generator for a set of values.
    """

    config = GeneratorConfig(1, True, False)

    def __call__(self) -> Set[Any]:
        return set(super().__call__())


class TupleSequenceGenerator(SequenceGenerator):
    """
    Generator for a tuple of values.
    """

    config = GeneratorConfig(1, True, True)

    def __call__(self) -> Tuple[Any]:
        return tuple(super().__call__())


class RangeGenerator(Generator):
    """
    Generator for ranges.
    """

    config = GeneratorConfig(0, True, True)

    def __init__(self, minimum: int = -2 ** 8, maximum: int = 2 ** 8, min_step: int = -2 ** 4, max_step: int = 2 ** 4):
        """
        Constructor.

        Args:
            minimum: The minimum value for the range (including).
            maximum: The maximum value for the range (including).
            min_step: The minimum step for the range (including).
            max_step: The maximum step for the range (including).
        """
        self.minimum = minimum
        self.maximum = maximum
        self.min_step = min_step
        self.max_step = max_step

    def __call__(self) -> range:
        start = random.randint(self.minimum, self.maximum - 1)
        stop = random.randint(start + 1, self.maximum)
        step = random.choice([x for x in range(self.min_step, self.max_step) if x != 0 and abs(x) <= abs(start - stop)])
        start, stop = sorted((start, stop), reverse=step < 0)
        return range(start, stop, step)


class OptionalGenerator(Generator):
    """
    Generator for optional values.
    """

    config = GeneratorConfig(1, True, True)

    def __init__(self, sub_generator: Generator, null_chance: float = 0.5):
        """
        Constructor.

        Args:
            sub_generator: The generator to use for generating a value.
            null_chance: The change of generating a None value, a float between 0 and 1.
        """
        self.null_chance = null_chance
        self.sub_generator = sub_generator

    def __call__(self) -> Optional[Any]:
        return None if random.random() < self.null_chance else self.sub_generator()


class DictGenerator(Generator):
    """
    Generator for a dictionary of values.
    """

    config = GeneratorConfig(2, True, False)

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
        self.keys_generator = keys_generator
        self.values_generator = values_generator
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self) -> Dict[Any, Any]:
        return {self.keys_generator(): self.values_generator() for _ in
                range(random.randint(self.min_length, self.max_length))}


class TupleGenerator(Generator):
    """
    Generator for a tuple of values of different types.
    """

    config = GeneratorConfig(-1, True, True)

    def __init__(self, sub_generators: Sequence[Generator]):
        """
        Constructor.

        Args:
            sub_generators: The generators to use for generating the tuple.
        """
        self.sub_generators = sub_generators

    def __call__(self) -> Tuple:
        return tuple(generator() for generator in self.sub_generators)


class TransformGenerator(Generator):
    """
    Generator for running a transformation.
    """

    config = GeneratorConfig(1, False, False)

    def __init__(self, sub_generator: Generator, transformer: Callable[[Any], Any]):
        """
        Constructor.

        Args:
            sub_generator: The generator to use for generating the initial value.
            transformer: The transformation to run on the value received from the generator.
        """
        self.sub_generator = sub_generator
        self.transformer = transformer

    def __call__(self) -> Any:
        return self.transformer(self.sub_generator())


# All the available generators.
GENERATORS = [
    IntGenerator,
    FloatGenerator,
    StringGenerator,
    BytesGenerator,
    RangeGenerator,
    SequenceGenerator,
    ListGenerator,
    TupleSequenceGenerator,
    SetGenerator,
    OptionalGenerator,
    DictGenerator,
    TupleGenerator,
    GeneratorCollection,
    ChooseGenerator,
    FixedGenerator,
    TransformGenerator
]


class AnyGenerator(Generator):
    """
    Generator for every possible value.
    """

    config = GeneratorConfig(-1, True, True)

    def __init__(self, sub_generators: Sequence[Generator] = None, max_depth: int = 5, require_hashable: bool = False):
        self.sub_generator = self.generate_generator(sub_generators, max_depth, require_hashable)

    @staticmethod
    def generate_generator(given_generator_options: List[Generator] = None, max_depth: int = 5,
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

        if chosen_generator == SetGenerator:
            return chosen_generator(AnyGenerator.generate_generator(given_generator_options, max_depth - 1, True))
        if chosen_generator == DictGenerator:
            return chosen_generator(AnyGenerator.generate_generator(given_generator_options, max_depth - 1, True),
                                    AnyGenerator.generate_generator(given_generator_options, max_depth - 1,
                                                                    require_hashable))

        if chosen_generator.config.sub_generators_number == -1:
            return chosen_generator(
                [AnyGenerator.generate_generator(given_generator_options, max_depth - 1, require_hashable) for _ in
                 range(random.randint(1, 10))])

        return chosen_generator(
            *[AnyGenerator.generate_generator(given_generator_options, max_depth - 1, require_hashable) for _ in
              range(chosen_generator.config.sub_generators_number)])

    def __call__(self) -> Any:
        return self.sub_generator()


GENERATORS.append(AnyGenerator)


class TypingGeneratorFactory:
    """
    A factory for generating generators from type annotations.
    """

    # Mapping of final typing annotation and the matching generator initialization.
    FINAL_ANNOTATION_TO_GENERATOR = {
        int: partial(IntGenerator),
        float: partial(FloatGenerator),
        complex: partial(FloatGenerator),
        bool: partial(BoolGenerator),
        str: partial(StringGenerator),
        bytes: partial(BytesGenerator),
        range: partial(RangeGenerator),
        object: partial(AnyGenerator),

        list: lambda: ListGenerator(AnyGenerator()),
        dict: lambda: DictGenerator(AnyGenerator(require_hashable=True), AnyGenerator()),
        set: lambda: SetGenerator(AnyGenerator(require_hashable=True)),
        tuple: lambda: TupleSequenceGenerator(AnyGenerator()),

        typing.List: lambda: ListGenerator(AnyGenerator()),
        typing.Dict: lambda: DictGenerator(AnyGenerator(require_hashable=True), AnyGenerator()),
        typing.Set: lambda: SetGenerator(AnyGenerator(require_hashable=True)),
        typing.Tuple: lambda: TupleSequenceGenerator(AnyGenerator()),
        typing.Any: partial(AnyGenerator),
        typing.Optional: lambda: OptionalGenerator(AnyGenerator())
    }

    # Mapping of continuous typing annotation and the matching generator.
    CONTINUOUS_ANNOTATION_TO_GENERATOR = {
        typing.List: ListGenerator,
        typing.Dict: DictGenerator,
        typing.Set: SetGenerator,
        typing.Tuple: TupleGenerator,
        typing.Any: AnyGenerator,
        typing.Optional: Optional,
        typing.Union: GeneratorCollection
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

                args_generators = [TypingGeneratorFactory.get_generator(arg) for arg in args]
                matching_generator = TypingGeneratorFactory.CONTINUOUS_ANNOTATION_TO_GENERATOR[origin]
                return matching_generator(args_generators) if \
                    matching_generator.config.sub_generators_number == -1 else \
                    matching_generator(*args_generators)

        raise ValueError(f'Could not interpret type "{annotation}".')

    @staticmethod
    def get_generators(func: Callable) -> Dict[str, Generator]:
        """
        Get generators for a function by its type annotations.

        Args:
            func: The function to get generators for.

        Returns:
            The generators matching the function's type annotations.
        """
        params = signature(func).parameters
        # todo: maybe check also .kind of the parameter, like POSITIONAL_OR_KEYWORD.
        return {name: TypingGeneratorFactory.get_generator(type_.annotation) for name, type_ in params.items()}
