from .models import Ranking
from .utils import find_first_index, get_attr_or_item, math_round

__all__ = (
    'get_tierlist_rank',
    'get_leaderboard_rank',
)


def get_tierlist_rank(ranking: Ranking, buildscore: float) -> int:
    return find_first_index(get_attr_or_item(ranking, 'ranks'), buildscore)


def _leaderboard_comp_func(a: float, b: float) -> bool:
    return math_round(a, 4) >= math_round(b, 4)


def get_leaderboard_rank(ranking: Ranking, buildscore: float) -> int:
    return find_first_index(get_attr_or_item(ranking, 'leaderboard'), buildscore, _leaderboard_comp_func)
