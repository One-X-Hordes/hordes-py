from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Optional

from ..buildscore import get_buildscore
from ..effects import Effect, Effects
from ..entity import Entity, EntityStats
from ..item import Item
from ..utils import MISSING
from .elo import Elo
from .prestige import Prestige
from .slots import MutableSlots, SlotsProxy
from .statpoints import STATPOINTS_PER_LEVEL, MutableStatpoints, StatpointsProxy

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..models import CharacterDict, CharacterModel
    from ..types.character import ClassId, FactionId

# fmt: off
__all__ = (
    'Character',
)
# fmt: on

BLOODLINES = (0, 3, 2, 4)

DEFAULT_STATS = {
    0: 10,
    1: 10,
    2: 10,
    3: 10,
    4: 10,
    5: 5,
    6: 100,
    7: 100,
    8: 20,
    9: 30,
    12: 15,
    14: 50,
    15: 105,
    17: 10,
    19: 15,
}

EQUIP_SLOT_IDS = frozenset({101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111})


class Character(Entity):
    class_id: ClassId

    def __init__(
        self,
        name: str,
        class_id: ClassId,
        faction_id: FactionId,
        level: int,
        prestige: int = 0,
        elo: int = 1500,
        id: Optional[int] = None,
    ) -> None:
        super().__init__(name=name, level=level, faction_id=faction_id, id=id)
        self.class_id = class_id

        self._elo = Elo(elo)
        self._prestige = Prestige(prestige)
        self._slots = MutableSlots()
        self._statpoints = MutableStatpoints()

        self.set_effects(Effect(61 + self.class_id, level=1, stacks=1))

    @property
    def elo(self) -> Elo:
        return self._elo

    def set_elo(self, value: int) -> None:
        self._elo = Elo(value)
        self._reload_stats()

    @property
    def prestige(self) -> Prestige:
        return self._prestige

    def set_prestige(self, value: int) -> None:
        self._prestige = Prestige(value)
        self._reload_stats()

    @property
    def statpoints(self) -> StatpointsProxy:
        return StatpointsProxy(self._statpoints)

    def clear_statpoints(self) -> None:
        self._statpoints.clear_statpoints()
        self._reload_stats()

    def add_statpoints(self, data: Mapping[int, int], *, strict: bool = True) -> None:
        if strict and sum(data.values()) > self.statpoints_available:
            raise ValueError(f'Attempted to assign {sum(data.values())} points while {self.statpoints_available} available')

        for id, value in data.items():
            self._statpoints.add_statpoints(id, value)
        self._reload_stats()

    @property
    def statpoints_available(self) -> int:
        return int(self._stats[22])

    @property
    def slots(self) -> SlotsProxy:
        return SlotsProxy(self._slots)

    def clear_items(self) -> None:
        self._slots.clear_items()
        self._reload_stats()

    def set_items(self, *items: Item, strict: bool = True) -> None:
        for item in items:
            if strict:
                if item.class_id and item.class_id != self.class_id:
                    continue
                elif item.level > self.level:
                    continue

            self._slots.set_item(item)

        self._reload_stats()

    def _set_stats(self, stats: EntityStats, *, tierlist: bool = False, **kwargs: Any) -> None:
        super()._set_stats(stats, tierlist=tierlist, **kwargs)

        for id, value in DEFAULT_STATS.items():
            stats[id] += value

        prestige = self.prestige if not tierlist else Prestige(48000)

        # Stats from level
        stats[1] += 2 * self.level
        stats[6] += 8 * self.level
        stats[BLOODLINES[self.class_id]] += self.level

        # Prestige
        stats += prestige.get_stats()

        # Items
        gearscore = 0
        for slot in EQUIP_SLOT_IDS:
            item = self.slots[slot]
            if item:
                for stat in item.stats:
                    stats[stat.id] += stat.value
                gearscore += item.gearscore

        # Statpoints
        for id, value in self._statpoints:
            stats[id] += value

        # Additional
        stats[22] = self.level * STATPOINTS_PER_LEVEL - self._statpoints.used
        stats[25] = gearscore
        stats[26] = min(45, max(self.level, (gearscore ** (5 / 6)) / 3.6))

    def _reload_stats(self, *, effects: Optional[Effects] = MISSING, tierlist: bool = False, **kwargs: Any) -> EntityStats:
        if not tierlist:
            tierlist_effects = Effects()
            for effect in filter(lambda x: x.id - 61 == self.class_id, self.effects):
                tierlist_effects.set_effect(effect)

            tierlist_stats = self._reload_stats(tierlist=True, effects=tierlist_effects)
            overall_score = tierlist_stats[107]
        else:
            overall_score = None

        stats = super()._reload_stats(effects=effects, tierlist=tierlist, **kwargs)

        buildscore = get_buildscore(stats, class_id=self.class_id)
        stats[101] = buildscore.dps
        stats[102] = buildscore.burst
        stats[103] = buildscore.ehp
        stats[104] = buildscore.dps_score
        stats[105] = buildscore.tank_score
        stats[106] = buildscore.hybrid_score
        stats[107] = overall_score or buildscore.overall_score

        return stats

    @classmethod
    def from_dataclass(cls, data: CharacterModel) -> Self:
        return cls(data.name, data.pclass, data.faction, data.level, data.prestige, data.elo, data.id)

    def to_dict(self) -> CharacterDict:
        return CharacterDict(
            name=self.name,
            pclass=self.class_id,
            faction=self.faction_id,
            level=self.level,
            prestige=int(self.prestige),
            elo=int(self.elo),
            id=self.id,
            fame=0,
            clan=None,
            gs=None,
        )
