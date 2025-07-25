from typing import Iterator, SupportsIndex

from ..data import STATPOINTS_ID_RANGE

__all__ = ()


class Statpoints:
    _statpoints: list[int]

    def __init__(self):
        self._statpoints = [0] * STATPOINTS_ID_RANGE

    @property
    def used(self) -> int:
        return sum(self._statpoints)

    def to_dict(self) -> dict[int, int]:
        return {id: value for id, value in self}

    def __getitem__(self, key: SupportsIndex) -> int:
        return self._statpoints[key]

    def __iter__(self) -> Iterator[tuple[int, int]]:
        return enumerate(self._statpoints)


class StatpointsProxy(Statpoints):
    def __init__(self, statpoints: Statpoints) -> None:
        self._statpoints = statpoints._statpoints


class MutableStatpoints(Statpoints):
    def add_statpoints(self, id: int, amount: int) -> None:
        self.__setitem__(id, amount)

    def clear_statpoints(self) -> None:
        for id, _ in self:
            self.__setitem__(id, 0)

    def __setitem__(self, key: SupportsIndex, value: int) -> None:
        if key not in range(STATPOINTS_ID_RANGE):
            raise KeyError(f'Stat Points must be in range of {STATPOINTS_ID_RANGE}.')

        return self._statpoints.__setitem__(key, value)
