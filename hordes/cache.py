from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Iterable, TypeVar, overload

if TYPE_CHECKING:
    from .types.common import SupportsKeysAndGetItem


__all__ = (
    'LRUDict',
    'BytesCache',
)

KT = TypeVar('KT')
VT = TypeVar('VT')


class LRUDict(OrderedDict[KT, VT]):
    """`dict` with Least Recent Used order of items."""

    def __setitem__(self, key: KT, value: VT) -> None:
        super().__setitem__(key, value)
        self.move_to_end(key, last=True)

    def __getitem__(self, key: KT) -> VT:
        value = super().__getitem__(key)
        self.move_to_end(key, last=True)

        return value


class SizedCache(LRUDict[KT, VT]):
    # Reused overloads from dict type stubs licensed under Apache 2.0 by typeshed
    @overload
    def __init__(self, *, max_size: int) -> None: ...
    @overload
    def __init__(self, map: SupportsKeysAndGetItem[KT, VT], /, *, max_size: int) -> None: ...
    @overload
    def __init__(self, iterable: Iterable[tuple[KT, VT]], /, *, max_size: int) -> None: ...

    # Next two overloads are for dict(string.split(sep) for string in iterable)
    # Cannot be Iterable[Sequence[T]] or otherwise dict(["foo", "bar", "baz"]) is not an error
    @overload
    def __init__(
        self: dict[str, str],
        iterable: Iterable[list[str]],
        /,
        *,
        max_size: int,
    ) -> None: ...
    @overload
    def __init__(
        self: dict[bytes, bytes],
        iterable: Iterable[list[bytes]],
        /,
        *,
        max_size: int,
    ) -> None: ...

    def __init__(self, *args: Any, max_size: int, **kwargs: Any):
        if isinstance(max_size, int) and not (max_size > 0):
            raise ValueError(f'Expected size to be more than 0, received {max_size}')

        super().__init__(*args, **kwargs)

        self.max_size = max_size

    def __setitem__(self, key, value) -> None:
        super().__setitem__(key, value)

        while len(self) > self.max_size:
            self.__delitem__(next(iter(self)))


class BytesCache(LRUDict[KT, bytes]):
    # Reused overloads from dict type stubs licensed under Apache 2.0 by typeshed
    @overload
    def __init__(self, *, max_size: int) -> None: ...
    @overload
    def __init__(self, map: SupportsKeysAndGetItem[KT, VT], /, *, max_size: int) -> None: ...
    @overload
    def __init__(self, iterable: Iterable[tuple[KT, VT]], /, *, max_size: int) -> None: ...

    # Next two overloads are for dict(string.split(sep) for string in iterable)
    # Cannot be Iterable[Sequence[T]] or otherwise dict(["foo", "bar", "baz"]) is not an error
    @overload
    def __init__(
        self: dict[str, str],
        iterable: Iterable[list[str]],
        /,
        *,
        max_size: int,
    ) -> None: ...
    @overload
    def __init__(
        self: dict[bytes, bytes],
        iterable: Iterable[list[bytes]],
        /,
        *,
        max_size: int,
    ) -> None: ...

    def __init__(self, *args: Any, max_size: int, **kwargs: Any):
        if isinstance(max_size, int) and not (max_size > 0):
            raise ValueError(f'Expected size to be more than 0, received {max_size}')

        super().__init__(*args, **kwargs)

        self.max_size = max_size

        self._size: int = sum([len(i) for i in self.values()])

    def __setitem__(self, key: KT, value: bytes) -> None:
        super().__setitem__(key, value)

        self._size += len(value)

        while self._size > self.max_size:
            self.__delitem__(next(iter(self)))

    def __delitem__(self, key: KT) -> None:
        value = self.get(key)

        super().__delitem__(key)

        if value:
            self._size -= len(value)
