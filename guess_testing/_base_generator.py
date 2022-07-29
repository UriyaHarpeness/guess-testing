from __future__ import annotations

import abc
import inspect
from dataclasses import dataclass
from typing import Generic, Iterable, List, TypeVar


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
        return [generator for generator in cls.__subclasses__() if not inspect.isabstract(generator)]

    # @abc.abstractmethod
    # def matches_requirements(self, requirements: Iterable[object]) -> bool:
    #     pass

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
    """
    Base class for the generators.
    """

    __slots__ = ()

    @property
    @abc.abstractmethod
    def generated_type(self) -> object:
        raise NotImplementedError

    # @abc.abstractmethod
    # def matches_requirements(self, requirements: Iterable[object]) -> bool:
    #     pass
