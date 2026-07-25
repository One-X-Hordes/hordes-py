from .models import Ranking
from .stats import Stats
from .utils import find_first_index, get_attr_or_item, math_round

__all__ = (
    'get_tierlist_rank',
    'get_leaderboard_rank',
)


def get_tierlist_rank(ranking: Ranking, stats: Stats) -> int:
    overall_stat: int = get_attr_or_item(ranking, 'overall')
    brackets: dict[int, list[float]] = get_attr_or_item(ranking, 'brackets')

    ranks: list[float] = brackets.get(overall_stat, [])
    score = stats[overall_stat]
    try:
        return (len(ranks) - 1) - find_first_index(ranks, score)
    except IndexError:
        return 0


def _leaderboard_comp_func(a: float, b: float) -> bool:
    return math_round(a, 4) >= math_round(b, 4)


def get_leaderboard_rank(ranking: Ranking, stats: Stats) -> int:
    overall_stat: int = get_attr_or_item(ranking, 'overall')

    leaderboard: list[float] = get_attr_or_item(ranking, 'leaderboard')
    score = stats[overall_stat]
    try:
        return find_first_index(leaderboard, score, _leaderboard_comp_func)
    except IndexError:
        return len(leaderboard)
