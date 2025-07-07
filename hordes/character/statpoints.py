from typing import Iterator, SupportsIndex

__all__ = (
    'STATPOINTS_PER_LEVEL',
    'STATPOINTS_ID_RANGE',
)

STATPOINTS_PER_LEVEL = 3
STATPOINTS_ID_RANGE = 6


class Statpoints:
    _statpoints: list[int]

    def __init__(self):
        self._statpoints = [0] * STATPOINTS_ID_RANGE

    @property
    def used(self) -> int:
        return sum(self._statpoints)

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
