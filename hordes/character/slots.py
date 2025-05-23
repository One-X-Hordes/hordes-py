from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..item import Item


class Slots:
    _slots: dict[int, Union[Item, None]]

    def __init__(self) -> None:
        self._slots = dict()

    def __getitem__(self, key: int) -> Union[Item, None]:
        return self._slots.get(key, None)

    def __iter__(self):
        return self._slots.__iter__()


class SlotsProxy(Slots):
    def __init__(self, slots: Slots) -> None:
        self._slots = slots._slots


class MutableSlots(Slots):
    def set_item(self, item: Item) -> None:
        slot = item.slot[-1]
        for id in item.slot:
            taken = self.__getitem__(id)
            if not taken:
                slot = id

        return self.__setitem__(slot, item)

    def remove_item(self, slot: int) -> None:
        return self.__setitem__(slot, None)

    def clear_items(self) -> None:
        for slot in self._slots:
            self.remove_item(slot)

    def __setitem__(self, key: int, item: Union[Item, None]) -> None:
        return self._slots.__setitem__(key, item)
