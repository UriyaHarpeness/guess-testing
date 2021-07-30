import abc
import random
import typing
from dataclasses import dataclass
from functools import partial
from inspect import signature
from typing import Any, Callable, Dict
from typing import Generator as GeneratorT
from typing import List, Optional, Sequence, Set, Tuple


class Generator(abc.ABC):
    @abc.abstractmethod
    def __call__(self) -> Any:
        pass

    def __str__(self) -> str:
        return '%s(%r)' % (self.__class__, self.__dict__)

    def __repr__(self) -> str:
        return str(self)


class IntGenerator(Generator):
    def __init__(self, start: int = -2 ** 20, stop: int = 2 ** 20, step: int = 1):
        self.start = start
        self.stop = stop
        self.step = step

    def __call__(self) -> int:
        return random.randrange(self.start, self.stop, self.step)


class FloatGenerator(Generator):
    def __init__(self, start: float = -2 ** 20, stop: float = 2 ** 20, step: Optional[float] = None):
        self.start = start
        self.stop = stop
        self.step = step

    def __call__(self) -> float:
        if not self.step:
            return random.uniform(self.start, self.stop)
        return random.randrange(int(self.start / self.step), int(self.stop / self.step)) * self.step


class BoolGenerator(Generator):
    def __call__(self) -> bool:
        return random.choice((True, False))


class StringGenerator(Generator):
    UPPERCASE = ''.join(chr(x) for x in range(ord('A'), ord('Z') + 1))
    LOWERCASE = ''.join(chr(x) for x in range(ord('a'), ord('z') + 1))
    NUMBERS = ''.join(chr(x) for x in range(ord('0'), ord('9') + 1))
    READABLE_OTHER = '!@#$%^&*()-=_+{}[]\\|/<>\'"`~;.,\n\t '
    ALL = ''.join(chr(x) for x in range(256))
    READABLE = UPPERCASE + LOWERCASE + NUMBERS + READABLE_OTHER

    def __init__(self, min_length: int = 0, max_length: int = 2 ** 5, selection: str = READABLE):
        self.min_length = min_length
        self.max_length = max_length
        self.selection = selection

    def __call__(self) -> str:
        return ''.join(
            random.choice(self.selection) for _ in range(random.randrange(self.min_length, self.max_length + 1)))


class BytesGenerator(StringGenerator):
    def __call__(self) -> bytes:
        return super().__call__().encode('utf-8')


class ChoiceGenerator(Generator):
    def __init__(self, options: Sequence[Generator]):
        self.options = options

    def __call__(self) -> Any:
        return random.choice(self.options)()


class ChooseGenerator(Generator):
    def __init__(self, options: Sequence[Any]):
        self.options = options

    def __call__(self) -> Any:
        return random.choice(self.options)


class FixedGenerator(Generator):
    def __init__(self, value: Any):
        self.value = value

    def __call__(self) -> Any:
        return self.value


class GeneratorCollection(Generator):
    def __init__(self, sub_generators: Sequence[Generator]):
        self.sub_generators = sub_generators

    def __call__(self) -> Any:
        return random.choice(self.sub_generators)()


class SequenceGenerator(Generator):
    def __init__(self, sub_generator: Generator, min_length: int = 0, max_length: int = 2 ** 4):
        self.sub_generator = sub_generator
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self) -> GeneratorT[Any, Any, Any]:
        return (self.sub_generator() for _ in range(random.randint(self.min_length, self.max_length)))


class ListGenerator(SequenceGenerator):
    def __call__(self) -> List[Any]:
        return list(super().__call__())


class SetGenerator(SequenceGenerator):
    def __call__(self) -> Set[Any]:
        return set(super().__call__())


class TupleSequenceGenerator(SequenceGenerator):
    def __call__(self) -> Tuple[Any]:
        return tuple(super().__call__())


class RangeGenerator(Generator):
    def __init__(self, minimum: int = -2 ** 8, maximum: int = 2 ** 8, min_step: int = -2 ** 4, max_step: int = 2 ** 4):
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
    def __init__(self, sub_generator: Generator, null_chance: float = 0.5):
        self.null_chance = null_chance
        self.sub_generator = sub_generator

    def __call__(self) -> Optional[Any]:
        return None if random.random() < self.null_chance else self.sub_generator()


class DictGenerator(Generator):
    def __init__(self, keys_generator: Generator, values_generator: Generator, min_length: int = 0,
                 max_length: int = 2 ** 4):
        self.keys_generator = keys_generator
        self.values_generator = values_generator
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self) -> Dict[Any, Any]:
        return {self.keys_generator(): self.values_generator() for _ in
                range(random.randint(self.min_length, self.max_length))}


class TupleGenerator(Generator):
    def __init__(self, sub_generators: Sequence[Generator]):
        self.sub_generators = sub_generators

    def __call__(self) -> Tuple:
        return tuple(generator() for generator in self.sub_generators)


class TransformGenerator(Generator):
    def __init__(self, sub_generator: Generator, transformer: Callable[[Any], Any]):
        self.sub_generator = sub_generator
        self.transformer = transformer

    def __call__(self) -> Any:
        return self.transformer(self.sub_generator())


@dataclass
class GeneratorConfig:
    sub_generators_number: int
    is_fixed_generator: bool
    immutable: bool


GENERATORS_CONFIGS = {
    IntGenerator: GeneratorConfig(0, False, True),
    FloatGenerator: GeneratorConfig(0, False, True),
    BoolGenerator: GeneratorConfig(0, False, True),
    StringGenerator: GeneratorConfig(0, False, True),
    BytesGenerator: GeneratorConfig(0, False, True),
    RangeGenerator: GeneratorConfig(0, False, True),

    SequenceGenerator: GeneratorConfig(1, False, False),
    ListGenerator: GeneratorConfig(1, False, False),
    TupleSequenceGenerator: GeneratorConfig(1, False, True),
    SetGenerator: GeneratorConfig(1, False, False),
    OptionalGenerator: GeneratorConfig(1, False, True),

    DictGenerator: GeneratorConfig(2, False, False),

    TupleGenerator: GeneratorConfig(-1, False, True),
    ChoiceGenerator: GeneratorConfig(-1, False, True),
    GeneratorCollection: GeneratorConfig(-1, False, True),

    ChooseGenerator: GeneratorConfig(-1, True, True),

    FixedGenerator: GeneratorConfig(1, True, True),

    TransformGenerator: GeneratorConfig(1, True, False)
}


class AnyGenerator(Generator):
    def __init__(self, max_depth: int = 5, require_hashable: bool = False):
        self.sub_generator = self.generate_generator(max_depth, require_hashable)

    @staticmethod
    def generate_generator(max_depth: int = 5, require_hashable: bool = False) -> Generator:
        generator_options = [(generator, config) for generator, config in GENERATORS_CONFIGS.items() if
                             not config.is_fixed_generator]

        if require_hashable:
            generator_options = [(generator, config) for generator, config in generator_options if config.immutable]

        if max_depth <= 1:
            generator_options = [(generator, config) for generator, config in generator_options if
                                 not config.is_fixed_generator and config.sub_generators_number == 0]

        chosen_generator, chosen_generator_config = random.choice(generator_options)

        if chosen_generator == SetGenerator:
            return chosen_generator(AnyGenerator.generate_generator(max_depth - 1, True))
        if chosen_generator == DictGenerator:
            return chosen_generator(AnyGenerator.generate_generator(max_depth - 1, True),
                                    AnyGenerator.generate_generator(max_depth - 1, require_hashable))

        if chosen_generator_config.sub_generators_number == -1:
            return chosen_generator([AnyGenerator.generate_generator(max_depth - 1, require_hashable) for _ in
                                     range(random.randint(1, 10))])

        return chosen_generator(*[AnyGenerator.generate_generator(max_depth - 1, require_hashable) for _ in
                                  range(chosen_generator_config.sub_generators_number)])

    def __call__(self) -> Any:
        return self.sub_generator()


class TypingGeneratorFactory:
    MAPPING = {
        int: partial(IntGenerator),
        float: partial(FloatGenerator),
        complex: partial(FloatGenerator),
        bool: partial(BoolGenerator),
        str: partial(StringGenerator),
        bytes: partial(StringGenerator),
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

    TYPING_TRANSLATION = {
        typing.List: ListGenerator,
        typing.Dict: DictGenerator,
        typing.Set: SetGenerator,
        typing.Tuple: TupleGenerator,
        typing.Any: AnyGenerator,
        typing.Optional: Optional,
        typing.Union: ChoiceGenerator
    }

    @staticmethod
    def get_generator(annotation: type) -> Generator:
        # todo: maybe support more typing types.
        if annotation in TypingGeneratorFactory.MAPPING:
            return TypingGeneratorFactory.MAPPING[annotation]()

        if annotation.__module__ == 'typing':
            origin, args = annotation.__origin__, annotation.__args__
            if origin in TypingGeneratorFactory.TYPING_TRANSLATION:
                if not args:
                    return TypingGeneratorFactory.MAPPING[annotation]()

                args_generators = [TypingGeneratorFactory.get_generator(arg) for arg in args]
                matching_generator = TypingGeneratorFactory.TYPING_TRANSLATION[origin]
                return matching_generator(args_generators) if \
                    GENERATORS_CONFIGS[matching_generator].sub_generators_number == -1 else \
                    matching_generator(*args_generators)

        raise ValueError(f'Could not interpret type "{annotation}".')

    @staticmethod
    def get_generators(func: Callable) -> Dict[str, Generator]:
        params = signature(func).parameters
        # todo: maybe check also .kind of the parameter, like POSITIONAL_OR_KEYWORD.
        return {name: TypingGeneratorFactory.get_generator(type_.annotation) for name, type_ in params.items()}
