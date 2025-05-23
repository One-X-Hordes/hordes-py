from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generator, Optional, Union

from .utils import MISSING

if TYPE_CHECKING:
    from .stats import MutableStats


__all__ = (
    'Effect',
    'Effects',
)


class Effect:
    logic: EffectLogic

    def __init__(self, id: int, *, level: int, stacks: int, caster: int = MISSING):
        self.id = id
        self.level = level
        self.stacks = stacks
        self.caster = caster

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
        static: Optional[Callable[[Effect, MutableStats], Any]] = None,
        convert: Optional[tuple[tuple[int, float, int], ...]] = None,
    ):
        self.id = id
        self.unique = unique
        self.passive = passive

        self.static = static
        self.convert = convert


EffectsLogic = {
    i.id: i
    for i in [
        EffectLogic(
            id=59,
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
        ),
        EffectLogic(
            id=63,
            passive=True,
        ),
        EffectLogic(
            id=64,
            passive=True,
        ),
        EffectLogic(
            id=66,
            static=lambda effect, stats: (stats.add_stat(30, effect.level * 9)),
        ),
    ]
}
