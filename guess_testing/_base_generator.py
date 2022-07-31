from __future__ import annotations

import abc
import inspect
from dataclasses import dataclass
from typing import Generic, Iterable, List, TypeVar, get_origin, Optional, Tuple, Mapping, Any, Callable, get_args, \
    Union


@dataclass
class RequiresSpecification:
    to_resolve: Tuple[Union[Tuple[int, type], type], ...]
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
    def handle_specification(cls, specification: type) -> Optional[RequiresSpecification]:
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


class ConcreteGenerator(Generic[_T], Generator[_T], metaclass=abc.ABCMeta):
    __slots__ = ()

    @property
    @classmethod
    @abc.abstractmethod
    def generated_type(cls) -> type:
        raise NotImplementedError

    @classmethod
    def matches_specification(cls, specification: type) -> bool:
        if specification.__module__ == 'typing':
            origin = get_origin(specification)
            if origin is not None:
                try:
                    return issubclass(cls.generated_type, origin)
                except TypeError:
                    return False

        return issubclass(cls.generated_type, specification)


class FinalConcreteGenerator(Generic[_T], ConcreteGenerator[_T], metaclass=abc.ABCMeta):
    __slots__ = ()

    @classmethod
    def handle_specification(cls, specification: type, /) -> Optional[RequiresSpecification]:
        if not cls.matches_specification(specification) or get_args(specification):
            return None
        return RequiresSpecification((), cls, ((), {}))

    def __str__(self) -> str:
        return self.generated_type.__name__
