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

ITEM_EXPRESSION = re.compile(r'(?P<type>[A-Za-z]+)(?P<percent>\d+)t(?P<tier>\d+)(?P<stats>(?:[A-Za-z]+\d+\.*\d){0,4})')
STAT_EXPRESSION = re.compile(r'(?P<name>[A-Za-z]+)(?P<percent>\d+\.*\d)')


def parse_custom_item(input_string: str) -> ParsedCustomItem:
    res = ITEM_EXPRESSION.search(input_string)

    if not res:
        raise ValueError('Invalid input string format')

    item_type = res['type'].lower()
    item_percent = int(res['percent'])
    item_tier = int(res['tier'])

    stats: list[ItemRawStatDict] = []

    for match in STAT_EXPRESSION.finditer(res['stats']):
        stat_name = match['name']
        stat_percent = float(match['percent'])

        if len(stat_name) > 1:
            stat_name = stat_name.lower()

        if stat_name in STAT_IDS:
            stat_id = STAT_IDS[stat_name]

            stats.append({'id': stat_id, 'percent': stat_percent})

    return {
        'percent': item_percent,
        'tier': item_tier,
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
