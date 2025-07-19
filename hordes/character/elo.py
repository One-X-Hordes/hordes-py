from ..data import ELO_RANKS

__all__ = ()


def get_elo_rank(value: int, /) -> int:
    rank = 0
    for i, req in enumerate(ELO_RANKS):
        if value >= req:
            rank = i

    return rank


class Elo:
    def __init__(self, value: int, /) -> None:
        self._value = value
        self._rank = get_elo_rank(value)

    @property
    def value(self) -> int:
        return self._value

    @property
    def rank(self) -> int:
        return self._rank

    def __int__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} value={self.value} rank={self.rank}>'
