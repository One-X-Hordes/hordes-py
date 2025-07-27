from ..data import PRESTIGE_RANKS, Stat
from ..stats import MutableStats

__all__ = ()

PRESTIGE_BUFFS: tuple[tuple[tuple[int, int], ...], ...] = (
    ((Stat.MoveSpeed, 5),),
    ((Stat.MP, 50),),
    ((Stat.ItemFind, 15),),
    ((Stat.MinDmg, 5), (Stat.MaxDmg, 5)),
    ((Stat.HPReg, 20), (Stat.MPReg, 20)),
    ((Stat.MoveSpeed, 5),),
    ((Stat.HP, 30),),
    ((Stat.ItemFind, 15),),
    ((Stat.Critical, 50),),
    ((Stat.Haste, 30),),
    ((Stat.HP, 30),),
    ((Stat.MinDmg, 5), (Stat.MaxDmg, 5)),
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
