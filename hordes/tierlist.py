from .models import Ranking
from .utils import get_attr_or_item, iter_index


def get_tierlist_rank(ranking: Ranking, buildscore: float) -> int:
    return iter_index(get_attr_or_item(ranking, 'ranks'), buildscore)


def get_leaderboard_rank(ranking: Ranking, buildscore: float) -> int:
    return iter_index(get_attr_or_item(ranking, 'leaderboard'), buildscore)
