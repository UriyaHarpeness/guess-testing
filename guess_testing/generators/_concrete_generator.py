from __future__ import annotations

import abc
import collections.abc
import inspect
from typing import Generic, Any, Set, TypeVar, Hashable

from guess_testing.generators._base_generator import Generator, TypeSpecification, TypeSpec

_T = TypeVar('_T')


def requires_hashable_explicitly(specification: TypeSpec) -> bool:
    return TypeSpecification.get_origin(specification) in {Hashable, collections.abc.Hashable} or \
           'hashable' in TypeSpecification.get_qualifiers(specification)


def handle_qualifiers_by_typing(specification: TypeSpec) -> Set[str]:
    qualifiers = TypeSpecification.get_qualifiers(specification).copy()
    if requires_hashable_explicitly(specification):
        qualifiers.add('hashable')
    return qualifiers


class ConcreteGenerator(Generic[_T], Generator[_T], metaclass=abc.ABCMeta):
    __slots__ = ()

    @property
    @classmethod
    @abc.abstractmethod
    def generated_type(cls) -> type:
        raise NotImplementedError

    @property
    @classmethod
    @abc.abstractmethod
    def supported_qualifiers(cls) -> Set[str]:
        raise NotImplementedError

    @property
    @classmethod
    @abc.abstractmethod
    def unsupported_disqualifiers(cls) -> Set[str]:
        raise NotImplementedError

    @classmethod
    def _matches_specification(cls, specification: type) -> bool:
        origin = TypeSpecification.get_origin(specification)
        if not inspect.isclass(origin):
            return False

        if TypeSpecification.is_any(origin):
            origin = object

        qualifiers = handle_qualifiers_by_typing(specification)
        if qualifiers - cls.supported_qualifiers:
            return False

        disqualifiers = TypeSpecification.get_disqualifiers(specification)
        if disqualifiers & cls.unsupported_disqualifiers:
            return False

        return issubclass(cls.generated_type, origin)
