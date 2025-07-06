from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from ..types.character import ClassId, FactionId
    from ..types.item import ItemType

    Localization = Mapping[str, Any]


BOUND_NAMES = ('', 'AC', 'CB')
QUALITY_NAMES = ('common', 'uncommon', 'rare', 'epic', 'legendary', 'legendary')
TIERLIST_RANK_NAMES = ('SSS', 'SS', 'S', 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'E', 'F')


def get_class_name(locale: Localization, /, id: ClassId) -> str:
    return locale['classes'][id]['name']


def get_faction_name(locale: Localization, /, id: FactionId) -> str:
    return locale['factions'][id]['name']


def get_prestige_rank_name(locale: Localization, /, faction: FactionId, rank: int) -> str:
    return locale['ui']['title']['name'][faction][rank]


def get_tierlist_rank_name(rank: int) -> str:
    return TIERLIST_RANK_NAMES[rank]


def get_charpanel_strings(locale: Localization, /) -> tuple[str, ...]:
    charpanel = locale['ui']['charpanel']
    return (
        charpanel['name'],
        charpanel['level'],
        charpanel['class'],
        charpanel['faction'],
        get_stat_name(locale, 20),
        charpanel['rating'],
        charpanel['rank'],
    )


def get_charpanel_keys(rank: bool = False) -> tuple[str | int, ...]:
    keys = ['name', 'level', 'class', 'faction', 20, 'rating']

    if rank:
        keys.append('rank')

    return tuple(keys)


def get_row_name(locale: Localization, /, key: str | int) -> str:
    if isinstance(key, str):
        return locale['ui']['charpanel'][key]
    if isinstance(key, int):
        return get_stat_name(locale, key)


def get_item_name(locale: Localization, /, item_type: ItemType, tier: int) -> str:
    return locale['items'][item_type][tier]['name']


def get_stat_name(locale: Localization, /, id: int) -> str:
    if id > 100:
        return ('DPS', 'Burst', 'Effective HP', 'DPS Score', 'Tank Score', 'Hybrid Score', 'Build Score')[id - 101]

    return locale['ui']['stats']['array'][id]
