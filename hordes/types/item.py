from typing import Literal, TypedDict

BoundId = Literal[0, 1, 2]
ItemType = Literal[
    'hammer',
    'bow',
    'staff',
    'sword',
    'armlet',
    'armor',
    'bag',
    'boot',
    'glove',
    'ring',
    'amulet',
    'quiver',
    'shield',
    'totem',
    'orb',
    'rune',
    'misc',
    'book',
    'charm',
    'mount',
    'box',
    'pet',
    'material',
    'gold',
]
Rolls = list[int]


class ItemRawStatDict(TypedDict):
    id: int
    percent: float


class ItemStatDict(ItemRawStatDict):
    value: float
    type: Literal['main', 'sub']
