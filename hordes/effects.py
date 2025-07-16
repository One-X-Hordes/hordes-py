from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, Callable, Generator, Optional, Union

from .utils import MISSING

if TYPE_CHECKING:
    from .stats import MutableStats

# fmt: off
__all__ = (
    'Effect',
)
# fmt: on


class Effect:
    logic: EffectLogic

    def __init__(self, id: int, *, level: int, stacks: int, caster: int = MISSING):
        self.id = id
        self.level = level
        self.stacks = stacks
        self.caster = caster

        self.active = True
        self.unique_instances = 0

        self.logic = EffectsLogic[id]


class Effects:
    _effects: dict[int, dict[int, Effect]]

    def __init__(self) -> None:
        self._effects = dict()

    def set_effect(self, effect: Effect) -> None:
        effect_dict = self._effects.get(effect.id, {})  # How to deal with rev stacks?
        effect_dict.__setitem__(effect.caster, effect)

        self._effects.__setitem__(effect.id, effect_dict)

    def get_effect(self, id: int, *, caster: int = MISSING) -> Union[Effect, None]:
        return self._effects.get(id, {}).get(caster, None)

    def remove_effect(self, id: int, *, caster: int = MISSING) -> None:
        effect_dict = self._effects[id]
        effect_dict.__delitem__(caster)

        if len(effect_dict) == 0:
            self._effects.__delitem__(id)

    def update_unique(self, id: int) -> None:
        effect_dict = self._effects[id]

        if effect_dict:
            current: Effect | None = None
            for effect in effect_dict.values():
                if not current or effect.level > current.level:
                    current = effect

                effect.active = False
                effect.unique_instances = len(effect_dict)
            if current:
                current.active = True

    def clear_effects(self) -> None:
        for effect_dict in self._effects.values():
            effect_dict.clear()
        return self._effects.clear()

    def __iter__(self) -> Generator[Effect]:
        for effect_dict in self._effects.values():
            for effect in effect_dict.values():
                yield effect

    def __len__(self) -> int:
        return self._effects.__len__()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} len={self.__len__()}>'


class EffectLogic:
    def __init__(
        self,
        *,
        id: int,
        unique: bool = False,
        passive: bool = False,
        icon: Optional[str] = None,
        static: Optional[Callable[[Effect, MutableStats], Any]] = None,
        convert: Optional[tuple[tuple[int, float, int], ...]] = None,
    ):
        self.id = id
        self.unique = unique
        self.passive = passive
        self.icon = icon

        self.static = static
        self.convert = convert


EffectsLogic = {
    i.id: i
    for i in [
        EffectLogic(
            id=59,
            icon='ui/skills/2',
            static=lambda effect, stats: (stats.add_stat(13, 300 + effect.level * 40)),
        ),
        EffectLogic(
            id=61,
            passive=True,
            convert=((0, 0.3, 10), (0, 0.3, 11), (0, 0.3, 8)),
        ),
        EffectLogic(
            id=62,
            passive=True,
            convert=((3, 0.4, 10), (3, 0.4, 11)),
        ),
        EffectLogic(
            id=63,
            passive=True,
            convert=((2, 0.4, 10), (2, 0.4, 11)),
        ),
        EffectLogic(
            id=64,
            passive=True,
            convert=((4, 0.4, 10), (4, 0.4, 11)),
        ),
        EffectLogic(
            id=66,
            icon='ui/skills/11',
            static=lambda effect, stats: (stats.add_stat(30, effect.level * 9)),
        ),
        EffectLogic(
            id=71,
            icon='ui/skills/16',
            static=lambda effect, stats: (
                stats.add_stat(16, 30 + effect.level * 70),
                stats.add_stat(30, 2 + effect.level * 8),
            ),
        ),
        EffectLogic(
            id=72,
            icon='ui/skills/17',
            static=lambda effect, stats: (stats.add_stat(30, effect.level * 12)),
        ),
        EffectLogic(
            id=75,
            unique=True,
            icon='ui/skills/19',
            static=lambda effect, stats: (
                stats.add_stat(10, effect.level * 3),
                stats.add_stat(11, effect.level * 4),
                stats.add_stat(6, effect.level * 50),
            ),
        ),
        EffectLogic(
            id=76,
            unique=True,
            icon='ui/skills/20',
            static=lambda effect, stats: (
                stats.add_stat(12, effect.level * 30),
                stats.add_stat(9, effect.level * 22),
            ),
        ),
        EffectLogic(
            id=77,
            icon='ui/skills/21',
            static=lambda effect, stats: (
                stats.add_stat(12, effect.level * 40),
                stats.add_stat(31, effect.level * 200),
            ),
        ),
        EffectLogic(
            id=78,
            unique=True,
            icon='ui/skills/22',
            static=lambda effect, stats: (stats.add_stat(14, effect.level * 30)),
        ),
        EffectLogic(
            id=80,
            unique=True,
            icon='ui/skills/24',
            static=lambda effect, stats: (
                stats.add_stat(10, math.floor(2 + effect.level * 1.5)),
                stats.add_stat(11, math.floor(3 + effect.level * 3.5)),
            ),
        ),
        EffectLogic(
            id=81,
            unique=True,
            icon='ui/skills/25',
            static=lambda effect, stats: (stats.add_stat(16, effect.level * 30)),
        ),
        EffectLogic(
            id=82,
            icon='ui/skills/26',
            static=lambda effect, stats: (stats.add_stat(14, effect.level * 30)),
        ),
        EffectLogic(
            id=84,
            unique=True,
            icon='ui/skills/28',
            static=lambda effect, stats: (stats.add_stat(16, 100 + effect.level * 60)),
        ),
        EffectLogic(
            id=107,
            icon='ui/skills/43',
            static=lambda effect, stats: (stats.add_stat(16, (10 + effect.level * 20) * 5)),
        ),
        EffectLogic(
            id=110,
            icon='ui/skills/charm2',
            static=lambda effect, stats: (stats.add_stat(30, 20)),
        ),
        EffectLogic(
            id=135,
            icon='items/charm/charm6_q1',
            static=lambda effect, stats: (stats.add_stat(16, 150)),
        ),
        EffectLogic(
            id=137,
            icon='items/charm/charm7_q1',
            static=lambda effect, stats: (stats.add_stat(30, 20)),
        ),
        EffectLogic(
            id=145,
            icon='items/charm/charm14_q1',
            static=lambda effect, stats: (stats.add_stat(18, 110 if effect.level >= 2 else 10 if effect.level == 1 else 0)),
        ),
    ]
}
