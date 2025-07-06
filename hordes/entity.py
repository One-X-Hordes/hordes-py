from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any, MutableMapping, Optional, Union

from .effects import Effect, Effects
from .stats import MutableStats, StatsProxy
from .utils import MISSING, math_round

if TYPE_CHECKING:
    from typing_extensions import Self

    from .types.character import FactionId


# fmt: off
__all__ = (
    'Entity',
)
# fmt: on

CONVERTABLE_STATS: dict[int, dict[int, Union[int, float]]] = {
    0: {
        6: 2,
        8: 0.3,
    },
    1: {
        6: 4,
        12: 1,
    },
    2: {
        14: 0.5,
    },
    3: {
        14: 0.4,
        7: 0.8,
    },
    4: {
        16: 0.3,
        7: 0.8,
    },
    5: {
        14: 0.2,
        18: 0.4,
    },
}


def apply_converts(mapping: Union[MutableMapping[int, float], MutableStats], *converts: tuple[int, float, int]) -> None:
    for id, gain, gain_id in converts:
        value = mapping.get(gain_id, 0) if isinstance(mapping, dict) else mapping[gain_id]
        mapping[gain_id] = value + mapping[id] * gain


def convert(mapping: MutableStats) -> None:
    mapping[6] += mapping[0] * 2 + mapping[1] * 4
    mapping[7] += int(mapping[3] * 0.8) + math_round(mapping[4] * 0.8)
    mapping[8] += mapping[0] * 0.3
    mapping[12] += mapping[1] * 1
    mapping[14] += int(mapping[2] * 0.5) + int(mapping[3] * 0.4) + math_round(mapping[5] * 0.2)
    mapping[16] += math_round(mapping[4] * 0.3)
    mapping[18] += mapping[5] * 0.4


class EntityStats(MutableStats):
    def __init__(self):
        super().__init__()
        self.evaluated: bool = False
        self._layers: dict[int, dict[int, float]] = {}
        self._effect: Union[Effects, None] = None

    def reset(self) -> None:
        self.evaluated = False
        self._layers.clear()
        self._effects = None
        return super().reset()

    def _apply_effects(self, effects: Effects) -> None:
        for effect in effects:
            logic = effect.logic

            # Static
            if logic.static:
                logic.static(effect, self)

            # Convert
            if logic.convert:
                apply_converts(self, *logic.convert)

    def get_gains(self, id: int, amount: int) -> dict[int, float]:
        if not self.evaluated:
            raise  # Add proper error here

        gains: dict[int, float] = defaultdict(lambda: 0)

        if id in CONVERTABLE_STATS:
            for gain_id, gain in CONVERTABLE_STATS[id].items():
                gains[gain_id] += gain * amount

        elif id == 30:  # Special case
            for key in (10, 11):
                gains[key] = self._layers[1][key] * (1 + amount / 100)

        if self._effects:
            for effect in self._effects:
                logic = effect.logic
                if logic.convert:
                    apply_converts(gains, *logic.convert)

        return dict(gains)

    def evaluate(self, *, effects: Optional[Effects] = None) -> Self:
        self._effects = effects

        convert(self)

        if effects:
            self._apply_effects(effects)

        self._layers[1] = dict(self._stats)

        self[10] *= 1 + self[30] / 100
        self[11] *= 1 + self[30] / 100

        self[10] = int(self[10])
        self[11] = math_round(self[11])

        self.evaluated = True
        return self


class Entity:
    faction_id: FactionId

    def __init__(self, name: str, level: int, faction_id: FactionId, id: Optional[int]) -> None:
        self.name = name
        self._level = level
        self.faction_id = faction_id
        self.id = id

        self._stats = EntityStats()
        self._effects = Effects()

    @property
    def level(self) -> int:
        return self._level

    def set_level(self, level: int) -> None:
        self._level = level
        self._reload_stats()

    @property
    def stats(self) -> StatsProxy:
        return StatsProxy(self._stats)

    def _set_stats(self, stats: EntityStats, **kwargs: Any) -> None: ...

    def _reload_stats(self, *, effects: Optional[Effects] = MISSING, **kwargs: Any) -> EntityStats:
        self._stats.reset()

        self._set_stats(self._stats, **kwargs)

        return self._stats.evaluate(effects=self.effects if effects is MISSING else effects)

    def get_stat_gains(self, id: int, amount: int) -> dict[int, float]:
        return self._stats.get_gains(id, amount)  # Proxy this method outside because it's not accessible on StatsProxy.

    @property
    def effects(self) -> Effects:
        return self._effects

    def set_effects(self, *effects: Effect) -> None:
        for effect in effects:
            self._effects.set_effect(effect)
        self._reload_stats()

    def clear_effects(self) -> None:
        self._effects.clear_effects()
        self._reload_stats()

    def remove_effect(self, id: int, *, caster: int = MISSING):
        self._effects.remove_effect(id, caster=caster)
        self._reload_stats()
