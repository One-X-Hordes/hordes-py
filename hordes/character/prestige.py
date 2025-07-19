from ..data import PRESTIGE_RANKS
from ..stats import MutableStats

__all__ = ()

PRESTIGE_BUFFS: tuple[tuple[tuple[int, int], ...], ...] = (
    ((15, 5),),
    ((7, 50),),
    ((18, 15),),
    ((10, 5), (11, 5)),
    ((8, 20), (9, 20)),
    ((15, 5),),
    ((6, 30),),
    ((18, 15),),
    ((14, 50),),
    ((16, 30),),
    ((6, 30),),
    ((10, 5), (11, 5)),
)


def get_prestige_rank(value: int, /) -> int:
    rank = 0
    for i, req in enumerate(PRESTIGE_RANKS):
        if value >= req:
            rank = i

    return rank


class Prestige:
    def __init__(self, value: int, /):
        self._value = value
        self._rank = get_prestige_rank(value)

    @property
    def value(self) -> int:
        return self._value

    @property
    def rank(self) -> int:
        return self._rank

    def get_stats(self) -> MutableStats:
        stats = MutableStats()

        for i in range(self.rank):
            for buff in PRESTIGE_BUFFS[i]:
                stats[buff[0]] += buff[1]

        return stats

    def __int__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} amount={self.value} rank={self.rank}>'
