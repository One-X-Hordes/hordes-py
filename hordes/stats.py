from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from typing_extensions import Self


__all__ = (
    'Stats',
    'StatsProxy',
    'MutableStats',
)


class Stats:
    _stats: dict[int, float]

    def __init__(self) -> None:
        self._stats = dict()

    def copy(self) -> Self:
        stats = self.__class__()
        stats._stats.update(self._stats)

        return stats

    def get_stat(self, id: int) -> float:
        return self.__getitem__(id)

    def __getitem__(self, key: int) -> float:
        return self._stats.get(key, 0)

    def __iter__(self) -> Iterator[tuple[int, float]]:
        return iter(self._stats.items())

    def __repr__(self) -> str:
        return self._stats.__repr__()

    def __len__(self) -> int:
        return self._stats.__len__()


class StatsProxy(Stats):
    def __init__(self, stats: Stats) -> None:
        self._stats = stats._stats


class MutableStats(Stats):
    def set_stat(self, id: int, value: float) -> None:
        return self.__setitem__(id, value)

    def add_stat(self, id: int, value: float) -> None:
        """Converts current stat to `int` and adds `value` to it.
        \nUse `__setitem__` if this behavior is not desirable."""
        self[id] = int(self[id]) + value

    def reset(self) -> None:
        self._stats.clear()

    def __setitem__(self, key: int, value: float) -> None:
        return self._stats.__setitem__(key, value)

    def __delitem__(self, key: int) -> None:
        return self._stats.__delitem__(key)

    def __add__(self, other: Stats) -> Self:
        if not isinstance(other, Stats):
            return NotImplemented

        stats = self.copy()
        stats += other

        return stats

    def __iadd__(self, other: Stats) -> Self:
        if not isinstance(other, Stats):
            return NotImplemented

        for key, value in other:
            self[key] += value

        return self

    def __sub__(self, other: Stats) -> Self:
        if not isinstance(other, Stats):
            return NotImplemented

        stats = self.copy()
        stats -= other

        return stats

    def __isub__(self, other: Stats) -> Self:
        if not isinstance(other, Stats):
            return NotImplemented

        for key, value in other:
            self[key] -= value

        return self
