from __future__ import annotations

import abc
import inspect
from dataclasses import dataclass
from typing import Generic, Iterable, List, TypeVar, get_origin, Optional, Tuple, Mapping, Any, Callable, get_args, \
    Union, Set


class TypeSpecification:
    def __init__(self, accepted: Optional[Union[Tuple[type, ...], type]] = None,
                 rejected: Optional[Union[Tuple[type, ...], type]] = None,
                 qualifiers: Optional[Set[str]] = None,
                 disqualifiers: Optional[Set[str]] = None):
        self.accepted, self.checkable_accepted = self.__parse_specifications(accepted, (object,))
        self.rejected, self.checkable_rejected = self.__parse_specifications(rejected, ())
        self.qualifiers = qualifiers or set()
        self.disqualifiers = disqualifiers or set()

    @staticmethod
    def get_origin(specification) -> type:
        if isinstance(specification, TypeSpecification):
            assert len(specification.accepted) == 1
            assert not specification.rejected
            specification = next(iter(specification.accepted))
        return get_origin(specification) or specification

    @staticmethod
    def get_args(specification) -> Tuple[type, ...]:
        if isinstance(specification, TypeSpecification):
            assert len(specification.accepted) == 1
            assert not specification.rejected
            specification = next(iter(specification.accepted))
        return get_args(specification)

    @staticmethod
    def get_qualifiers(specification) -> Set[str]:
        if not isinstance(specification, TypeSpecification):
            return set()
        return specification.qualifiers

    @staticmethod
    def get_disqualifiers(specification) -> Set[str]:
        if not isinstance(specification, TypeSpecification):
            return set()
        return specification.disqualifiers

    @staticmethod
    def is_any(specification) -> bool:
        return TypeSpecification.get_origin(specification) in {object, ..., Any}

    @staticmethod
    def __parse_specifications(specifications: Optional[Union[Tuple[type, ...], type]],
                               default_value: Tuple[type, ...]) -> Tuple[Tuple[type, ...], Tuple[type, ...]]:
        if specifications is None:
            specifications = default_value
        elif not isinstance(specifications, tuple):
            specifications = (specifications,)

        return specifications, tuple(get_origin(specification) or specification for specification in specifications)

    def __instancecheck__(self, instance: object) -> bool:
        return isinstance(instance, self.accepted) and not isinstance(instance, self.rejected)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'+({",".join(map(str, self.accepted))}) ' \
               f'-({",".join(map(str, self.rejected))}) ' \
               f'~+({",".join(self.qualifiers)}) ' \
               f'~-({",".join(self.disqualifiers)})'

    def __subclasscheck__(self, subclass: type) -> bool:
        return issubclass(subclass, self.checkable_accepted) and not issubclass(subclass, self.checkable_rejected)


TypeSpec = Union[type, TypeSpecification]


@dataclass
class RequiresSpecification:
    to_resolve: Tuple[Union[Tuple[Union[int, Callable[[], int]], TypeSpec], TypeSpec], ...]
    callback: Callable
    callback_arguments: Tuple[Iterable[Any], Mapping[str, Any]]


@dataclass(frozen=True)
class GeneratorConfig:
    """
    Configuration describing each generator.
    """

    sub_generators_number: int  # The number of sub generators the generator requires.
    requires_only_generators: bool  # Does the generator require only generators for initialization.
    immutable: bool  # Is the generator's result immutable.


_T = TypeVar('_T')


class Generator(Generic[_T], metaclass=abc.ABCMeta):
    """
    Base class for the generators.
    """

    __slots__ = ()

    @property
    @abc.abstractmethod
    def config(self) -> GeneratorConfig:
        """
        Configuration of the generator.
        """
        raise NotImplementedError

    @classmethod
    def get_inheritances(cls) -> List[Generator]:
        visited = set()
        to_visit = {cls}
        while to_visit:
            next_visit = to_visit.pop()
            to_visit.update(set(next_visit.__subclasses__()).difference(visited))
            visited.add(next_visit)
        return [generator for generator in visited if not inspect.isabstract(generator)]

    # @abc.abstractmethod
    @classmethod
    def handle_specification(cls, specification: type, /) -> Optional[RequiresSpecification]:
        return None

    @abc.abstractmethod
    def __call__(self) -> _T:
        """
        Generate a value.
        """

    def __repr__(self) -> str:
        """
        String representation of the generator.
        """
        return str(self)

    @abc.abstractmethod
    def __str__(self) -> str:
        """
        String representation of the generator.
        """
