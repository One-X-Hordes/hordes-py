from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired, Required

    from ..types.character import ClassId
    from ..types.item import ItemType

    class BonusStatLogicEntry(TypedDict):
        min: float
        max: float
        round: NotRequired[Literal[True]]

    class MainStatLogicStats(TypedDict):
        base: int
        min: float
        max: float

    MainStatLogic = TypedDict(
        'MainStatLogic',
        {
            'baselvl': int,
            'slot': tuple[int, ...],
            'tiers': int,
            'drop': float,
            'weight': float,
            'class': ClassId,
            'stats': dict[int, MainStatLogicStats],
            'stackable': bool,
            'quality': int,
            'noupgrade': bool,
            'undroppable': bool,
        },
        total=False,
    )

    class CharmLogic(TypedDict, total=False):
        custom: Required[list[str]]
        use_cd: int
        incap: bool
        anim_cast: int

    class ItemStatDataEntry(TypedDict):
        min: float
        max: float

    ItemLogicEntry = TypedDict(
        'ItemLogicEntry',
        {
            'level': Required[int],
            'type': Required[ItemType],
            'tier': Required[int],
            'quality': Required[Optional[int]],
            'stats': dict[int, ItemStatDataEntry],
            'class': ClassId,
            'gs': int,
            'unique_equipped': bool,
            'anim_cast': int,
            'incap': bool,
            'use_cd': int,
            'custom': list[str],
            'buy_elo': int,
            'gold_value': int,
            'medal_value': int,
            'use_skill': int,
        },
        total=False,
    )

    ItemLogic = dict[ItemType, dict[int, ItemLogicEntry]]


MAIN_STATS_LOGIC: dict[ItemType, MainStatLogic] = {
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


BONUS_STAT_LOGIC: dict[int, BonusStatLogicEntry] = {
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

CHARM_LOGIC: list[CharmLogic] = [
    {
        "custom": ["Use: Removes all movement limiting effects."],
        "use_cd": 60,
        "incap": True,
        "anim_cast": 45,
    },
    {
        "custom": ["Use: Protects you against 30% of incoming damage for 10 seconds."],
        "use_cd": 60,
        "anim_cast": 6,
        "incap": False,
    },
    {
        "custom": ["Use: Increases your damage by 20% for 10 seconds."],
        "use_cd": 80,
        "incap": False,
        "anim_cast": 6,
    },
    {
        "custom": ["Use: Speeds up your movement by 45 for 8 seconds."],
        "use_cd": 50,
        "incap": False,
        "anim_cast": 6,
    },
    {
        "custom": ["Use: Attacks made against you grant 20 MP (up to 200) for 20 seconds."],
        "use_cd": 60,
        "incap": False,
        "anim_cast": 6,
    },
    {
        "custom": ["Passive: Your attacks have a chance to heal you."],
    },
    {
        "custom": ["Passive: Your attacks have a chance to increase your haste by 15% for 12 seconds."],
    },
    {
        "custom": ["Passive: Increases your damage by 20% for 12 seconds when your health drops below 50%."],
    },
    {
        "custom": ["Use: Allows you to breathe underwater, swim faster and jump further while inside water."],
        "use_cd": 60,
        "incap": False,
        "anim_cast": 6,
    },
    {
        "custom": [
            "Use: Cover yourself in foliage, slowing your movement and turning you invisible to the enemy while standing still."
        ],
        "use_cd": 180,
        "incap": False,
        "anim_cast": 6,
    },
    {
        "custom": ["Use: Turns you into a miniature version of yourself, reducing fall damage by 50%."],
        "use_cd": 60,
        "incap": False,
        "anim_cast": 6,
    },
    {
        "custom": ["Use: The next ability you cast will have no cooldown."],
        "use_cd": 80,
        "incap": False,
        "anim_cast": 6,
    },
    {
        "custom": ["Use: Blocked attacks deal damage back to the enemy for 12 seconds."],
        "use_cd": 60,
        "incap": False,
        "anim_cast": 6,
    },
    {
        "custom": ["Use: Transforms you into an orc, granting daze immunity and +10 movement speed."],
        "use_cd": 60,
        "incap": False,
        "anim_cast": 6,
    },
    {
        "custom": ["Passive: Grants 10% Item Find + 1% for every 10 gold in your inventory. (100% Maximum)"],
    },
]

UPGRADE_GAINS: dict[int, float] = {
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


ITEM_LOGIC: ItemLogic = {}


def get_level(item_type: ItemType, tier: int) -> int:
    logic = MAIN_STATS_LOGIC[item_type]

    baselvl = logic.get('baselvl', 0)
    tiers = logic.get('tiers', 0)

    return baselvl + int(tier / tiers * 100)


def process_main(type: ItemType, data: MainStatLogic, obj: ItemLogic) -> None:
    if 'tiers' not in data:
        return

    for tier in range(data['tiers']):
        level = get_level(type, tier)

        res: ItemLogicEntry = {
            'level': level,
            'type': type,
            'tier': tier,
            'quality': data.get('quality'),
        }

        if 'class' in data:
            res['class'] = data['class']

        if 'stats' in data:
            res['stats'] = {}
            for key, value in data['stats'].items():
                res['stats'][key] = {
                    'min': value['base'] + level * value['min'],
                    'max': value['base'] + (level + 10) * value['max'],
                }

        if type not in obj:
            obj[type] = {}

        obj[type][tier] = res


def process_charm(data: CharmLogic, tier: int, obj: ItemLogic) -> None:
    type = 'charm'

    res: ItemLogicEntry = {
        **data,
        'level': 45,
        'type': type,
        'tier': tier,
        'quality': 90,
        'gs': 30,
        'unique_equipped': True,
    }

    if data.get('use_cd') is not None:
        res['use_skill'] = 107 + tier

    if tier <= 4:
        res['medal_value'] = 1000
        res['gold_value'] = 80_000
        res['buy_elo'] = 1600
    else:
        res['gold_value'] = 1_250_000

    if type not in obj:
        obj[type] = {}

    obj[type][tier] = res


def hydrate_data(obj: ItemLogic) -> None:
    for t, data in MAIN_STATS_LOGIC.items():
        process_main(t, data, obj)

    for t, data in enumerate(CHARM_LOGIC):
        process_charm(data, t, obj)


hydrate_data(ITEM_LOGIC)
