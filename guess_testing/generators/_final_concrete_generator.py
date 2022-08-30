from __future__ import annotations

import abc
from typing import Generic, Optional, TypeVar

from guess_testing.generators._base_generator import TypeSpecification, RequiresSpecification
from guess_testing.generators._concrete_generator import ConcreteGenerator

_T = TypeVar('_T')


class FinalConcreteGenerator(Generic[_T], ConcreteGenerator[_T], metaclass=abc.ABCMeta):
    __slots__ = ()

    @classmethod
    def handle_specification(cls, specification: type, /) -> Optional[RequiresSpecification]:
        if not cls._matches_specification(specification) or TypeSpecification.get_args(specification):
            return None
        return RequiresSpecification((), cls, ((), {}))

    def __str__(self) -> str:
        return self.generated_type.__name__
