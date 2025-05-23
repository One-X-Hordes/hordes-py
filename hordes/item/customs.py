from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING, Optional, TypedDict

from .stats import ItemStats, get_sub_stat_value

if TYPE_CHECKING:
    from ..types.item import ItemRawStatDict, ItemType

    class ParsedCustomItem(TypedDict):
        percent: int
        type: str
        tier: int
        stats: list[ItemRawStatDict]


__all__ = ()


STAT_CODES = {
    0: ['s', 'str', 'strength'],
    1: ['S', 'stam', 'stamina'],
    2: ['d', 'dex', 'dexterity'],
    3: ['i', 'int', 'intelligence'],
    4: ['w', 'wis', 'wisdom'],
    5: ['l', 'luck'],
    6: ['hp'],
    7: ['mp'],
    8: ['hpr'],
    9: ['mpr'],
    10: ['m', 'min'],
    11: ['M', 'max'],
    12: ['D', 'def', 'defense'],
    13: ['b', 'block'],
    14: ['c', 'crit', 'critical'],
    16: ['h', 'haste'],
    18: ['I', 'if'],
}

STAT_IDS = dict([(name, id) for id, names in STAT_CODES.items() for name in names])


# r'(?P<type>[A-Za-z]+)(?P<percent>\d+)t(?P<tier>\d+)(?P<stats>(?:[A-Za-z]+\d+\.*\d){0,4})' #TODO: Replace regex
def parse_custom_item(input_string: str) -> ParsedCustomItem:
    stat_names: list[str] = re.findall(r'[A-Za-z]+', input_string)
    stat_percents: list[str] = re.findall(r'\d+', input_string)
    item_type = stat_names[0].lower()

    percent = int(stat_percents[0])
    tier = int(stat_percents[1])

    stats: list[ItemRawStatDict] = []

    starter = 2
    index = starter

    while index < len(stat_names):
        stat = stat_names[index]
        if len(stat) > 1:
            stat = stat.lower()

        if stat in STAT_IDS:
            stat_id = STAT_IDS[stat]
            stat_percent = float(stat_percents[index])

            stats.append({'id': stat_id, 'percent': stat_percent})

        index += 1

    return {
        'percent': percent,
        'tier': tier,
        'type': item_type,
        'stats': stats,
    }


def round_stat_percent(percent: float, *, level: int, id: int, item_type: ItemType, upgrade: int = 0) -> int:
    value = get_sub_stat_value(level, id, item_type, percent, upgrade)
    rounded_value = get_sub_stat_value(level, id, item_type, round(percent), upgrade)

    if value > rounded_value:
        percent = int(percent)
    elif value < rounded_value:
        percent = math.ceil(percent)
    else:
        percent = round(percent)

    return percent


def generate_custom_item(
    *,
    item_type: ItemType,
    percent: int,
    tier: int,
    stats: Optional[ItemStats] = None,
    level: int,
    upgrade: int,
) -> str:
    base = [item_type, str(percent), 't', str(tier + 1)]

    if stats:
        for stat in stats:
            if stat.type != 'sub':
                continue

            code = STAT_CODES[stat.id][0]

            percent = round_stat_percent(
                stat.percent,
                id=stat.id,
                level=level,
                item_type=item_type,
                upgrade=upgrade,
            )

            base.extend([code, str(percent)])

    return ''.join(base)
