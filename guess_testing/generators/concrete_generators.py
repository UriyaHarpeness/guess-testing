import random
from types import GeneratorType
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple, Type, Union, Hashable, \
    runtime_checkable, Protocol

from guess_testing.generators._base_generator import Generator, GeneratorConfig, \
    RequiresSpecification, TypeSpecification
from guess_testing.generators._concrete_generator import ConcreteGenerator, handle_qualifiers_by_typing


# todo: break down this file, too long.

# todo: actually generator, not iterable... all the iterators and generators are hashable, but not all iterables.
class IterableGenerator(ConcreteGenerator[GeneratorType]):
    """
    Generator for iterable values.
    """

    generated_type = GeneratorType
    supported_qualifiers = set()
    unsupported_disqualifiers = set()
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

    @classmethod
    def handle_specification(cls, specification: type, /) -> Optional[RequiresSpecification]:
        if not cls._matches_specification(specification):
            return None

        args = TypeSpecification.get_args(specification)
        if not args:
            args = (object,)

        qualifiers = handle_qualifiers_by_typing(specification)

        return RequiresSpecification((TypeSpecification(accepted=args[0], qualifiers=qualifiers),), cls, ((), {}))

    def __call__(self) -> Iterable[object]:
        return (self._sub_generator() for _ in range(random.randint(self._min_length, self._max_length)))

    def __str__(self) -> str:
        return f'Iterable[{self._sub_generator}]'


class ListGenerator(IterableGenerator, ConcreteGenerator[list]):
    """
    Generator for a list of values.
    """

    generated_type = list
    supported_qualifiers = set()
    unsupported_disqualifiers = set()
    config = GeneratorConfig(1, True, False)

    __slots__ = ()

    def __call__(self) -> List[object]:
        return list(super().__call__())

    def __str__(self) -> str:
        return f'List[{self._sub_generator}]'


class SetGenerator(IterableGenerator, ConcreteGenerator[set]):
    """
    Generator for a set of values.
    """

    generated_type = set
    supported_qualifiers = set()
    unsupported_disqualifiers = set()
    config = GeneratorConfig(1, True, False)

    __slots__ = ()

    @classmethod
    def handle_specification(cls, specification: type, /) -> Optional[RequiresSpecification]:
        if not cls._matches_specification(specification):
            return None

        args = TypeSpecification.get_args(specification)
        if not args:
            args = (Hashable,)

        qualifiers = TypeSpecification.get_qualifiers(specification)

        return RequiresSpecification((TypeSpecification(accepted=args[0], qualifiers=qualifiers.union({'hashable'})),),
                                     cls, ((), {}))

    def __call__(self) -> Set[object]:
        return set(super().__call__())

    def __str__(self) -> str:
        return f'Set[{self._sub_generator}]'


class FrozenSetGenerator(SetGenerator, ConcreteGenerator[frozenset]):
    """
    Generator for a frozenset of values.
    """

    generated_type = frozenset
    supported_qualifiers = {'hashable'}
    unsupported_disqualifiers = set()
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
    supported_qualifiers = {'hashable'}
    unsupported_disqualifiers = set()
    config = GeneratorConfig(1, True, True)

    __slots__ = ()

    @classmethod
    def handle_specification(cls, specification: type, /) -> Optional[RequiresSpecification]:
        if not cls._matches_specification(specification):
            return None

        args = TypeSpecification.get_args(specification)
        if args and (len(args) != 2 or args[1] != Ellipsis):
            return None

        if not args:
            args = (object,)

        qualifiers = handle_qualifiers_by_typing(specification)

        return RequiresSpecification((TypeSpecification(accepted=args[0], qualifiers=qualifiers),), cls, ((), {}))

    def __call__(self) -> Tuple[object, ...]:
        return tuple(super().__call__())

    def __str__(self) -> str:
        return f'Tuple[{str(self._sub_generator)}, ...]'


class DictGenerator(ConcreteGenerator[dict]):
    """
    Generator for a dictionary of values.
    """

    generated_type = dict
    supported_qualifiers = set()
    unsupported_disqualifiers = set()
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

    @classmethod
    def handle_specification(cls, specification: type, /) -> Optional[RequiresSpecification]:
        if not cls._matches_specification(specification):
            return None

        args = TypeSpecification.get_args(specification)
        if not args:
            args = (Hashable, object)

        return RequiresSpecification((TypeSpecification(args[0], qualifiers={'hashable'}), args[1]), cls, ((), {}))

    def __call__(self) -> Dict[object, object]:
        return {self._keys_generator(): self._values_generator() for _ in
                range(random.randint(self._min_length, self._max_length))}

    def __str__(self) -> str:
        return f'Dict[{self._keys_generator}, {self._values_generator}]'


class TupleGenerator(ConcreteGenerator[Tuple[object, ...]]):
    """
    Generator for a tuple of values of different types.
    """

    generated_type = tuple
    supported_qualifiers = {'hashable'}
    unsupported_disqualifiers = set()
    config = GeneratorConfig(-1, True, True)

    __slots__ = ('_sub_generators',)

    def __init__(self, *sub_generators: Union[Sequence[Generator], Generator]):
        """
        Constructor.

        Args:
            sub_generators: The generators to use for generating the tuple.
        """
        self._sub_generators = []
        for sub_generator in sub_generators:
            if isinstance(sub_generator, list):
                self._sub_generators += sub_generator
            else:
                self._sub_generators.append(sub_generator)

    @classmethod
    def handle_specification(cls, specification: type, /) -> Optional[RequiresSpecification]:
        if not cls._matches_specification(specification):
            return None

        args = TypeSpecification.get_args(specification)
        if args and (len(args) == 2 and args[1] == Ellipsis):
            return None

        if not args:
            args = (object,)

        qualifiers = handle_qualifiers_by_typing(specification)

        return RequiresSpecification(
            tuple(TypeSpecification(accepted=arg, qualifiers=qualifiers) for arg in args), cls, ((), {}))

    def __call__(self) -> Tuple[object, ...]:
        return tuple(generator() for generator in self._sub_generators)

    def __str__(self) -> str:
        return f'Tuple[{", ".join(map(str, self._sub_generators))}]'
