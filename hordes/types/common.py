from pathlib import Path
from typing import Iterable, Protocol, TypeVar, Union

T = TypeVar("T")
KT = TypeVar("KT")  # Key type.
VT = TypeVar("VT")  # Value type.
T_co = TypeVar("T_co", covariant=True)  # Any type covariant containers.
KT_co = TypeVar("KT_co", covariant=True)  # Key type covariant containers.
VT_co = TypeVar("VT_co", covariant=True)  # Value type covariant containers.

StrOrNone = Union[str, None]
IntOrNone = Union[int, None]

StrPath = Union[str, Path]


class SupportsKeysAndGetItem(Protocol[KT, VT_co]):
    def keys(self) -> Iterable[KT]: ...
    def __getitem__(self, key: KT, /) -> VT_co: ...
