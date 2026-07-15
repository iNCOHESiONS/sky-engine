"""Unique sentinel values based on [PEP 661](https://peps.python.org/pep-0661/#reference-implementation)."""

from __future__ import annotations

import inspect
from types import UnionType
from typing import (
    LiteralString,
    Self,
    Union,  # pyright: ignore[reportDeprecated]
    final,
    override,
)

_sentinels: dict[str, Sentinel] = {}


def _get_calling_module_name() -> str:
    try:
        return (
            module.__name__
            if (module := inspect.getmodule(inspect.currentframe().f_back.f_back))  # pyright: ignore[reportOptionalMemberAccess]
            else __name__
        )
    except AttributeError:
        return __name__


@final
class Sentinel:
    """Unique sentinel values based on [PEP 661](https://peps.python.org/pep-0661/#reference-implementation)."""

    __slots__ = ("_id", "_repr")

    _id: str  # pyright: ignore[reportUninitializedInstanceVariable]
    _repr: str  # pyright: ignore[reportUninitializedInstanceVariable]

    @override
    def __new__(
        cls,
        name: LiteralString,
        /,
        *,
        module_name: str | None = None,
        repr: str | None = None,
    ) -> Sentinel:
        module = module_name or _get_calling_module_name()
        id = f"{module}-{name}"

        if cached := _sentinels.get(id, None):
            return cached

        sentinel = super().__new__(cls)
        sentinel._id = id
        sentinel._repr = repr or f'{cls.__name__}("{name}", module_name="{module}")'

        return _sentinels.setdefault(id, sentinel)

    def __init_subclass__(cls):
        raise TypeError("Sentinel cannot be used as a subclass")

    @override
    def __repr__(self) -> str:
        return self._repr

    @override
    def __reduce__(self) -> tuple[type[Self], tuple[str, str]]:
        return (self.__class__, (self.name, self.module))

    def __copy__(self) -> Self:
        return self

    def __deepcopy__(self, _) -> Self:
        return self

    def __or__(self, other: Self, /) -> UnionType:
        return Union[self, other]  # pyright: ignore[reportDeprecated]

    def __ror__(self, other: Self, /) -> UnionType:
        return Union[other, self]  # pyright: ignore[reportDeprecated]

    @property
    def name(self) -> str:
        """This `Sentinel`'s name."""

        return self._id.split("-")[-1]

    @property
    def module(self) -> str:
        """This `Sentinel`'s module's name."""

        return self._id.split("-")[0]
