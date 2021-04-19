import abc
import random
from typing import Any, Dict
from typing import Generator as GeneratorT
from typing import List, Optional, Sequence, Set, Tuple


class Generator(abc.ABC):
    @abc.abstractmethod
    def __call__(self):
        pass


class IntGenerator(Generator):
    def __init__(self, start: int, stop: int, step: int = 1):
        self.start = start
        self.stop = stop
        self.step = step

    def __call__(self) -> int:
        return random.randrange(self.start, self.stop, self.step)


class FloatGenerator(Generator):
    def __init__(self, start: float, stop: float, step: Optional[float] = None):
        self.start = start
        self.stop = stop
        self.step = step
        self.range = self.stop - self.start

    def __call__(self) -> float:
        if not self.step:
            return (random.random() * self.range) + self.start
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

    def __init__(self, min_length: int = 0, max_length: int = 20, selection: str = READABLE):
        self.min_length = min_length
        self.max_length = max_length
        self.selection = selection

    def __call__(self) -> str:
        return ''.join(
            random.choice(self.selection) for _ in range(random.randrange(self.min_length, self.max_length + 1)))


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
    def __init__(self, generators: Sequence[Generator]):
        self.generators = generators

    def __call__(self) -> Any:
        return random.choice(self.generators)()


class SequenceGenerator(Generator):
    def __init__(self, min_length: int, max_length: int, sub_generator: Generator):
        self.min_length = min_length
        self.max_length = max_length
        self.sub_generator = sub_generator

    def __call__(self) -> GeneratorT[Any, Any, Any]:
        return (self.sub_generator() for _ in range(random.randrange(self.min_length, self.max_length + 1)))


class ListGenerator(SequenceGenerator):
    def __call__(self) -> List[Any]:
        return list(super().__call__())


class TupleGenerator(SequenceGenerator):
    def __call__(self) -> Tuple[Any]:
        return tuple(super().__call__())


class SetGenerator(SequenceGenerator):
    def __call__(self) -> Set[Any]:
        return set(super().__call__())


class DictGenerator(Generator):
    def __init__(self, min_length: int, max_length: int, keys_generator: Generator, values_generator: Generator):
        self.min_length = min_length
        self.max_length = max_length
        self.keys_generator = keys_generator
        self.values_generator = values_generator

    def __call__(self) -> Dict[Any, Any]:
        return {self.keys_generator(): self.values_generator() for _ in
                range(random.randrange(self.min_length, self.max_length + 1))}
