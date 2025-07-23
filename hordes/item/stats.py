from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional, SupportsIndex, Union, overload

from .logic import BONUS_STAT_LOGIC, MAIN_STATS_LOGIC, UPGRADE_GAINS

if TYPE_CHECKING:
    from ..types.item import ItemRawStatDict, ItemStatDict, ItemStatType, Rolls
    from .logic import ItemLogicEntry

__all__ = ()


def get_rolls(stats: ItemStats, percent: int) -> Rolls:
    rolls = [percent]

    for stat in stats:
        if stat.type == 'bonus':
            rolls.extend([get_roll(stat.id), int(stat.percent * 2 - percent)])

    return rolls


class ItemStat:
    type: ItemStatType

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

    def __init__(self, logic: ItemLogicEntry, id: int, percent: int, upgrade: int = 0):
        super().__init__(
            id=id,
            percent=percent,
            value=get_main_stat_value(logic=logic, id=id, percent=percent, upgrade=upgrade),
        )


class BonusStat(ItemStat):
    type = 'bonus'

    def __init__(self, logic: ItemLogicEntry, id: int, percent: float, upgrade: int = 0):
        super().__init__(
            id=id,
            percent=percent,
            value=get_sub_stat_value(logic=logic, id=id, percent=percent, upgrade=upgrade),
        )


class ItemStats(Sequence[ItemStat]):
    _tuple: tuple[ItemStat, ...]

    def __init__(
        self,
        logic: ItemLogicEntry,
        percent: int,
        upgrade: int = 0,
        *,
        bonus: Optional[Sequence[ItemRawStatDict]] = None,
    ) -> None:

        stats: list[ItemStat] = []

        for id in logic.get('stats', {}):
            stats.append(MainStat(logic=logic, id=id, percent=percent, upgrade=upgrade))

        if bonus:
            for stat in bonus:
                stats.append(BonusStat(logic=logic, id=stat['id'], percent=stat['percent'], upgrade=upgrade))

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


def get_roll(id: int) -> int:
    keys = list(BONUS_STAT_LOGIC.keys())
    return math.ceil(keys.index(id) * 101 / len(keys))


def get_main_stat_value(logic: ItemLogicEntry, id: int, percent: int, upgrade: int = 0) -> int:
    assert 'stats' in logic

    stats = logic['stats']
    base_min = stats[id]['min']
    base_max = stats[id]['max']

    return int(base_min + (base_max - base_min) * pow(percent / 100, 2) + UPGRADE_GAINS[id] * upgrade)


def get_sub_stat_value(logic: ItemLogicEntry, id: int, percent: float, upgrade: int = 0) -> int:
    main_logic = MAIN_STATS_LOGIC[logic['type']]
    sub_logic = BONUS_STAT_LOGIC[id]

    assert 'weight' in main_logic

    level = logic['level']
    weight = main_logic['weight']

    value = math.ceil(
        max(
            (sub_logic['min'] + (sub_logic['max'] - sub_logic['min']) * pow(percent / 100, 2)) * level * weight,
            UPGRADE_GAINS[id],
        )
        + UPGRADE_GAINS[id] * upgrade
    )

    return value
