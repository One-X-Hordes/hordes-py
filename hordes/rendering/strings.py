from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from ..types.character import ClassId
    from ..types.item import ItemType

    Localization = Mapping[str, Any]


BOUND_NAMES = ('', 'AC', 'CB')
QUALITY_NAMES = ('common', 'uncommon', 'rare', 'epic', 'legendary', 'legendary')


def get_class_name(locale: Localization, /, id: ClassId) -> str:
    return locale['classes'][id]['name']


def get_item_name(locale: Localization, /, item_type: ItemType, tier: int) -> str:
    return locale['items'][item_type][tier]['name']


def get_stat_name(locale: Localization, /, id: int) -> str:
    return locale['ui']['stats']['array'][id]
