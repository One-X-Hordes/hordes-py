from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Sequence, Union

from ..models import ItemDict, ItemModel
from ..utils import MISSING, math_round
from .customs import generate_custom_item, parse_custom_item
from .stats import MAIN_STATS_DATA, SUB_STAT_DATA, UPGRADE_GAINS_DATA, ItemStats, get_rolls

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.character import ClassId
    from ..types.common import IntOrNone
    from ..types.item import BoundId, ItemRawStatDict, ItemType, Rolls


# fmt: off
__all__ = (
    'Item',
)
# fmt: on

MAX_ITEM_PERCENT = 110


class Item:
    _type: ItemType
    bound: BoundId
    _stats: ItemStats
    _gearscore: int

    def __init__(
        self,
        id: IntOrNone,
        item_type: ItemType,
        tier: int,
        percent: int,
        bound: BoundId,
        stats: Sequence[ItemRawStatDict],
        upgrade: Optional[int] = None,
        stacks: Optional[int] = None,
    ) -> None:
        if item_type not in MAIN_STATS_DATA:
            raise NotImplementedError(f'Item type {item_type} is not implemented.')

        self.id = id
        self._type = item_type
        self._tier = tier
        self._percent = percent
        self.bound = bound
        self._upgrade = upgrade
        self.stacks = stacks

        self._level = self._reload_level()

        self._stats, self._gearscore = self._reload_stats(additional=stats)

    def _reload_level(self) -> int:
        self._level = get_level(self.type, self.tier)
        return self._level

    def _reload_stats(self, additional: Optional[Sequence[ItemRawStatDict]] = MISSING) -> tuple[ItemStats, int]:
        if additional is MISSING:
            additional = self.stats.to_raw()

        self._stats = ItemStats(
            item_type=self.type,
            level=self.level,
            percent=self.percent,
            upgrade=self.upgrade or 0,
            additional=additional,
        )

        self._gearscore = get_gearscore(self)

        return self._stats, self._gearscore

    @property
    def type(self) -> ItemType:
        return self._type

    def set_type(self, /, item_type: ItemType) -> None:
        self._type = item_type
        self._reload_level()
        self._reload_stats()

    @property
    def tier(self) -> int:
        return self._tier

    def set_tier(self, /, tier: int) -> None:
        self._tier = tier
        self._reload_level()
        self._reload_stats()

    @property
    def percent(self) -> int:
        return self._percent

    def set_percent(self, /, percent: int) -> None:
        self._percent = percent
        self._reload_stats()

    @property
    def stats(self) -> ItemStats:
        return self._stats

    def set_stats(self, /, stats: list[ItemRawStatDict]) -> None:
        self._reload_stats(stats)

    @property
    def slot(self) -> tuple[int, ...]:
        return MAIN_STATS_DATA[self.type].get('slot', ())

    @property
    def class_id(self) -> Union[ClassId, None]:
        return MAIN_STATS_DATA[self.type].get('class', None)

    @property
    def upgrade(self) -> Union[int, None]:
        return self._upgrade

    def set_upgrade(self, /, upgrade: int) -> None:
        self._upgrade = upgrade
        self._reload_stats()

    @property
    def gearscore(self) -> int:
        return self._gearscore

    @property
    def level(self) -> int:
        return self._level

    @classmethod
    def from_dataclass(cls, data: ItemModel, upgrade: Optional[int] = None) -> Self:
        percent = data.rolls[0] if data.rolls else 0
        stats = get_stats_from_rolls(data.type, data.rolls) if data.rolls else {}
        upg = upgrade if isinstance(upgrade, int) else data.upgrade

        return cls(data.id, data.type, data.tier, percent, data.bound, list(stats.values()), upg, data.stacks)

    @classmethod
    def from_dict(cls, data: ItemDict, upgrade: Optional[int] = None) -> Self:
        percent = data['rolls'][0] if data['rolls'] else 0
        stats = get_stats_from_rolls(data['type'], data['rolls']) if data['rolls'] else {}
        upg = upgrade if isinstance(upgrade, int) else data['upgrade']

        return cls(data['id'], data['type'], data['tier'], percent, data['bound'], list(stats.values()), upg, data['stacks'])

    def to_dict(self) -> ItemDict:
        return ItemDict(
            id=self.id,
            slot=None,
            bound=self.bound,
            type=self.type,
            upgrade=self.upgrade,
            tier=self.tier,
            rolls=get_rolls(self.stats, self.percent),
            stacks=self.stacks,
        )

    @classmethod
    def from_generated(cls, input_string: str, upgrade: Optional[int] = 0) -> Self:
        data = parse_custom_item(input_string)

        item_type = data['type']

        if item_type not in MAIN_STATS_DATA:
            raise ValueError(f'Item type {item_type} is not implemented.')

        tier = min(data['tier'], MAIN_STATS_DATA[item_type].get('tiers', 1000)) - 1
        percent = min(data['percent'], MAX_ITEM_PERCENT)
        stats = data['stats'][: get_stats_amount(percent)]

        return cls(
            id=None,
            item_type=item_type,
            tier=tier,
            percent=percent,
            bound=0,
            stats=stats,
            upgrade=upgrade or 0,
        )

    def to_generated(self) -> str:
        return generate_custom_item(
            item_type=self.type,
            percent=self.percent,
            tier=self.tier,
            stats=self.stats,
            level=self.level,
            upgrade=self.upgrade or 0,
        )

    def __str__(self) -> str:
        base = [f'T{self.tier+1} {self.type.title()} {self.percent}%']

        if self.id:
            base.append(f'{self.id}')
        else:
            base.append(f'{self.to_generated()}')

        if self.upgrade and self.upgrade > 0:
            base.append(f'+{self.upgrade}')

        return ' '.join(base)


def get_stats_amount(percent: int):
    return min(4, round((percent / 100) ** 1.5 * 3.6))


def get_id(roll: int) -> int:
    keys = list(SUB_STAT_DATA.keys())
    return keys[int(roll / 101 * len(keys))]


def get_level(item_type: ItemType, tier: int) -> int:
    if item_type == 'charm':
        return 45

    logic = MAIN_STATS_DATA[item_type]

    baselvl = logic.get('baselvl', None)
    tiers = logic.get('tiers', None)

    if baselvl and tiers:
        return baselvl + int(tier / tiers * 100)
    else:
        return 0


def get_stats(item_type: ItemType, rolls: Union[Rolls, None]) -> dict[int, int]:
    stats: dict[int, int] = {}
    if not rolls:
        return stats

    item_logic = MAIN_STATS_DATA[item_type]
    main_stats = list(item_logic['stats'].keys()) if 'stats' in item_logic else []

    percent = rolls[0]
    stat_amount = get_stats_amount(percent)
    for i in range(1, stat_amount * 2 + 1, 2):
        roll = rolls[i]
        roll_percent = rolls[i + 1]

        stat_id = get_id(roll)

        while stat_id in stats or stat_id in main_stats:
            roll = (roll + 5) % 100
            stat_id = get_id(roll)

        stats[stat_id] = roll_percent

    return stats


def get_stats_from_rolls(item_type: ItemType, rolls: Rolls) -> dict[int, ItemRawStatDict]:
    stats: dict[int, ItemRawStatDict] = {}

    percent = rolls[0]
    _stats = get_stats(item_type, rolls)
    for id in _stats:
        roll_percent = _stats[id]
        stat_percent = (percent + roll_percent) / 2

        stats[id] = {'id': id, 'percent': stat_percent}

    return stats


def get_gearscore(item: Item) -> int:
    if item.type == 'charm':
        return 30

    gearscore = 0
    for stat in item.stats:
        if stat.id == 17:
            continue

        value = stat.value / UPGRADE_GAINS_DATA[stat.id]
        if item.type == 'shield' and stat.type == 'main':
            value *= 0.5
        if item.type == 'orb' and stat.type == 'main':
            value *= 0.7

        gearscore += value

    return math_round(gearscore)
