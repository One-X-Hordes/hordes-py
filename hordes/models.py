from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Protocol, TypedDict, Union

if TYPE_CHECKING:
    from .types.character import ClassId, FactionId
    from .types.common import IntOrNone
    from .types.item import BoundId, ItemType, Rolls


class CharacterDict(TypedDict):
    name: str
    pclass: ClassId
    faction: FactionId
    prestige: int
    level: int
    fame: Optional[int]
    clan: Optional[str]
    elo: int
    gs: Optional[int]
    id: Optional[int]


class ItemDict(TypedDict):
    id: Optional[int]
    slot: Optional[int]
    bound: BoundId
    type: ItemType
    upgrade: IntOrNone
    tier: int
    rolls: Union[Rolls, None]
    stacks: IntOrNone


class CharacterModel(Protocol):
    name: str
    pclass: ClassId
    faction: FactionId
    level: int
    prestige: int
    elo: int
    id: int


class ItemModel(Protocol):
    id: Optional[int]
    bound: BoundId
    type: ItemType
    upgrade: int
    tier: int
    rolls: Union[Rolls, None]
    stacks: IntOrNone


class TierlistRanking(Protocol):
    leaderboard: list[float]
    ranks: list[float]
