import abc
from dataclasses import dataclass
from typing import Any


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
