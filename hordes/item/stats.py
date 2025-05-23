from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal, Optional, SupportsIndex, TypedDict, Union, overload

if TYPE_CHECKING:
    from typing_extensions import NotRequired

    from ..types.character import ClassId
    from ..types.item import ItemRawStatDict, ItemStatDict, ItemType, Rolls

    class SubStatDataEntry(TypedDict):
        min: float
        max: float
        round: NotRequired[Literal[True]]

    class MainStatDataStats(TypedDict):
        base: int
        min: float
        max: float

    MainStatData = TypedDict(
        'MainStatData',
        {
            'baselvl': int,
            'slot': tuple[int, ...],
            'tiers': int,
            'drop': float,
            'weight': float,
            'class': ClassId,
            'stats': dict[int, MainStatDataStats],
            'stackable': bool,
            'quality': int,
            'noupgrade': bool,
            'undroppable': bool,
        },
        total=False,
    )


__all__ = ()


def get_rolls(stats: ItemStats, percent: int) -> Rolls:
    rolls = [percent]

    for stat in stats:
        if stat.type == 'sub':
            rolls.extend([get_roll(stat.id), int(stat.percent * 2 - percent)])

    return rolls


class ItemStat:
    type: Literal['main', 'sub']

    _id: int
    _percent: float
    _value: int

    def __init__(self, id: int, percent: float, value: int = 0) -> None:
        self._id = id
        self._percent = percent
        self._value = value

    @property
    def id(self) -> int:
        return self._id

    @property
    def percent(self) -> float:
        return self._percent

    @property
    def value(self) -> int:
        return self._value


class MainStat(ItemStat):
    type = 'main'

    def __init__(self, item_type: ItemType, level: int, id: int, percent: int, upgrade: int = 0):
        super().__init__(
            id=id,
            percent=percent,
            value=get_main_stat_value(level=level, id=id, item_type=item_type, percent=percent, upgrade=upgrade),
        )


class SubStat(ItemStat):
    type = 'sub'

    def __init__(self, item_type: ItemType, level: int, id: int, percent: float, upgrade: int = 0):
        super().__init__(
            id=id,
            percent=percent,
            value=get_sub_stat_value(level=level, id=id, item_type=item_type, percent=percent, upgrade=upgrade),
        )


class ItemStats(Sequence[ItemStat]):
    _tuple: tuple[ItemStat, ...]

    def __init__(
        self,
        item_type: ItemType,
        level: int,
        percent: int,
        upgrade: int = 0,
        *,
        additional: Optional[Sequence[ItemRawStatDict]] = None,
    ) -> None:

        logic = MAIN_STATS_DATA[item_type]
        stats: list[ItemStat] = []

        for id in logic.get('stats', {}):
            stats.append(MainStat(item_type, level=level, id=id, percent=percent, upgrade=upgrade))

        if additional:
            for stat in additional:
                stats.append(SubStat(item_type, level=level, id=stat['id'], percent=stat['percent'], upgrade=upgrade))

        self._tuple = tuple(stats)

    def to_raw(self) -> tuple[ItemStatDict, ...]:
        return tuple(
            {
                'id': stat.id,
                'percent': stat.percent,
                'value': stat.value,
                'type': stat.type,
            }
            for stat in self
        )

    @overload
    def __getitem__(self, index: SupportsIndex) -> ItemStat: ...

    @overload
    def __getitem__(self, index: slice) -> tuple[ItemStat, ...]: ...

    def __getitem__(self, index: Union[slice, SupportsIndex]) -> Union[ItemStat, tuple[ItemStat, ...]]:
        return self._tuple.__getitem__(index)

    def __len__(self) -> int:
        return self._tuple.__len__()


MAIN_STATS_DATA: dict[ItemType, MainStatData] = {
    'hammer': {
        'baselvl': 0,
        'slot': (101,),
        'tiers': 17,
        'drop': 0.4,
        'weight': 1,
        'class': 3,
        'stats': {
            10: {'base': 1, 'min': 0.6, 'max': 1},
            11: {'base': 3, 'min': 0.8, 'max': 1.7},
            17: {'base': 15, 'min': 0.05, 'max': 0.1},
        },
        'stackable': False,
    },
    'bow': {
        'baselvl': 0,
        'slot': (101,),
        'tiers': 17,
        'drop': 0.4,
        'weight': 1,
        'class': 2,
        'stats': {
            10: {'base': 1, 'min': 0.6, 'max': 1},
            11: {'base': 3, 'min': 0.8, 'max': 1.7},
            17: {'base': 10, 'min': 0.05, 'max': 0.1},
        },
        'stackable': False,
    },
    'staff': {
        'baselvl': 0,
        'slot': (101,),
        'tiers': 17,
        'drop': 0.4,
        'weight': 1,
        'class': 1,
        'stats': {
            10: {'base': 1, 'min': 0.6, 'max': 1},
            11: {'base': 3, 'min': 0.8, 'max': 1.7},
            17: {'base': 10, 'min': 0.05, 'max': 0.1},
        },
        'stackable': False,
    },
    'sword': {
        'baselvl': 0,
        'slot': (101,),
        'tiers': 17,
        'drop': 0.4,
        'weight': 1,
        'class': 0,
        'stats': {
            10: {'base': 1, 'min': 0.6, 'max': 1},
            11: {'base': 3, 'min': 0.8, 'max': 1.7},
            17: {'base': 20, 'min': 0.05, 'max': 0.1},
        },
        'stackable': False,
    },
    'armlet': {
        'baselvl': 1,
        'slot': (102,),
        'tiers': 13,
        'drop': 1,
        'weight': 0.3,
        'stats': {
            6: {'base': 10, 'min': 0.5, 'max': 0.9},
            12: {'base': 7, 'min': 0.5, 'max': 0.8},
        },
        'stackable': False,
    },
    'armor': {
        'baselvl': 2,
        'slot': (103,),
        'tiers': 11,
        'drop': 1,
        'weight': 1,
        'stats': {
            6: {'base': 20, 'min': 1, 'max': 2},
            12: {'base': 10, 'min': 1.4, 'max': 2.8},
        },
        'stackable': False,
    },
    'bag': {
        'baselvl': 5,
        'slot': (104,),
        'tiers': 5,
        'drop': 1,
        'weight': 0.1,
        'stats': {
            19: {'base': 1, 'min': 0.1, 'max': 0.3},
        },
        'stackable': False,
    },
    'boot': {
        'baselvl': 2,
        'slot': (105,),
        'tiers': 13,
        'drop': 1,
        'weight': 0.4,
        'stats': {
            6: {'base': 10, 'min': 0.6, 'max': 1},
            12: {'base': 8, 'min': 0.6, 'max': 1.1},
            15: {'base': 3, 'min': 0.03, 'max': 0.1},
        },
        'stackable': False,
    },
    'glove': {
        'baselvl': 2,
        'slot': (106,),
        'tiers': 13,
        'drop': 1,
        'weight': 0.4,
        'stats': {
            6: {'base': 10, 'min': 0.6, 'max': 1},
            12: {'base': 8, 'min': 0.7, 'max': 1.1},
            14: {'base': 1, 'min': 0.1, 'max': 1.5},
        },
        'stackable': False,
    },
    'ring': {
        'baselvl': 5,
        'slot': (107,),
        'tiers': 12,
        'drop': 0.8,
        'weight': 0.2,
        'stats': {
            6: {'base': 10, 'min': 0.5, 'max': 0.9},
            7: {'base': 5, 'min': 0.6, 'max': 1},
        },
        'stackable': False,
    },
    'amulet': {
        'baselvl': 7,
        'slot': (108,),
        'tiers': 12,
        'drop': 0.8,
        'weight': 0.3,
        'stats': {
            7: {'base': 10, 'min': 1, 'max': 1.8},
            9: {'base': 1, 'min': 0.2, 'max': 0.3},
        },
        'stackable': False,
    },
    'quiver': {
        'baselvl': 2,
        'slot': (109,),
        'tiers': 10,
        'drop': 0.7,
        'weight': 0.5,
        'class': 2,
        'stats': {
            9: {'base': 1, 'min': 0.1, 'max': 0.3},
            14: {'base': 5, 'min': 0.1, 'max': 0.9},
        },
        'stackable': False,
    },
    'shield': {
        'baselvl': 2,
        'slot': (109,),
        'tiers': 10,
        'drop': 0.7,
        'weight': 0.5,
        'class': 0,
        'stats': {
            12: {'base': 20, 'min': 0.8, 'max': 1.4},
            13: {'base': 4, 'min': 1, 'max': 2.8},
        },
        'stackable': False,
    },
    'totem': {
        'baselvl': 2,
        'slot': (109,),
        'tiers': 10,
        'drop': 0.7,
        'weight': 0.5,
        'class': 3,
        'stats': {
            9: {'base': 1, 'min': 0.1, 'max': 0.4},
            12: {'base': 10, 'min': 0.4, 'max': 0.9},
        },
        'stackable': False,
    },
    'orb': {
        'baselvl': 2,
        'slot': (109,),
        'tiers': 10,
        'drop': 0.7,
        'weight': 0.5,
        'class': 1,
        'stats': {
            3: {'base': 10, 'min': 0.3, 'max': 0.7},
            9: {'base': 1, 'min': 0.1, 'max': 0.3},
        },
        'stackable': False,
    },
    'rune': {
        'baselvl': 1,
        'tiers': 11,
        'drop': 0.8,
        'quality': 70,
        'stackable': True,
    },
    'misc': {
        'drop': 8,
        'weight': 0.1,
        'stackable': True,
    },
    'book': {
        'drop': 1.6,
        'weight': 0.5,
        'stackable': True,
    },
    'charm': {
        'slot': (110, 111),
        'noupgrade': True,
        'undroppable': True,
        'drop': 0,
        'stackable': False,
    },
    'mount': {
        'undroppable': True,
        'drop': 0,
        'stackable': False,
    },
    'box': {
        'noupgrade': True,
        'undroppable': True,
        'drop': 0,
        'stackable': False,
    },
    'pet': {
        'undroppable': True,
        'drop': 0,
        'stackable': False,
    },
    'material': {
        'drop': 0,
        'stackable': True,
    },
    'gold': {
        'drop': 24,
    },
}


SUB_STAT_DATA: dict[int, SubStatDataEntry] = {
    0: {'min': 0.08, 'max': 0.45, 'round': True},
    1: {'min': 0.08, 'max': 0.45, 'round': True},
    2: {'min': 0.08, 'max': 0.45, 'round': True},
    3: {'min': 0.08, 'max': 0.45, 'round': True},
    4: {'min': 0.08, 'max': 0.45, 'round': True},
    5: {'min': 0.08, 'max': 0.45, 'round': True},
    6: {'min': 0.2, 'max': 0.8, 'round': True},
    7: {'min': 0.2, 'max': 0.5, 'round': True},
    8: {'min': 0.1, 'max': 1},
    9: {'min': 0.1, 'max': 0.5},
    10: {'min': 0.03, 'max': 0.13, 'round': True},
    11: {'min': 0.1, 'max': 0.2, 'round': True},
    12: {'min': 0.1, 'max': 0.8, 'round': True},
    13: {'min': 0.1, 'max': 0.4},
    14: {'min': 0.1, 'max': 0.5},
    16: {'min': 0.1, 'max': 0.4},
    18: {'min': 0.01, 'max': 0.15, 'round': True},
}

UPGRADE_GAINS_DATA: dict[int, float] = {
    6: 4,
    7: 3,
    8: 5,
    9: 4,
    10: 1,
    11: 1,
    12: 5,
    13: 5,
    14: 5,
    15: 0.3,
    16: 5,
    17: 0,
    2: 2,
    0: 2,
    3: 2,
    4: 2,
    1: 2,
    5: 2,
    19: 1,
    18: 2.5,
}


def get_roll(id: int) -> int:
    keys = list(SUB_STAT_DATA.keys())
    return math.ceil(keys.index(id) * 101 / len(keys))


def get_main_stat_value(level: int, id: int, item_type: ItemType, percent: int, upgrade: int = 0) -> int:
    logic = MAIN_STATS_DATA[item_type]

    if 'stats' not in logic:
        return 0

    stats = logic['stats']
    stat = stats[id]

    base_min = stat['base'] + level * stat['min']
    base_max = stat['base'] + (level + 10) * stat['max']

    return int(base_min + (base_max - base_min) * pow(percent / 100, 2) + UPGRADE_GAINS_DATA[id] * upgrade)


def get_sub_stat_value(level: int, id: int, item_type: ItemType, percent: float, upgrade: int = 0) -> int:
    logic = SUB_STAT_DATA[id]
    item_logic = MAIN_STATS_DATA[item_type]

    if 'weight' not in item_logic:
        return 0

    weight = item_logic['weight']

    value = math.ceil(
        max((logic['min'] + (logic['max'] - logic['min']) * pow(percent / 100, 2)) * level * weight, UPGRADE_GAINS_DATA[id])
        + UPGRADE_GAINS_DATA[id] * upgrade
    )

    return value
