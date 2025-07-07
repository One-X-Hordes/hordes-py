from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ColorScheme:
    ELO: str
    PRESTIGE: str
    FACTIONS: tuple[str, ...]
    CLASSES: tuple[str, ...]
    ITEM_QUALITY: tuple[str, ...]
    STAT_QUALITY: tuple[str, ...]
    TIERLIST_RANK: tuple[str, ...]


@dataclass(frozen=True)
class ItemScheme(ColorScheme):
    BACKGROUND: str
    ID: str
    GS: str
    BOUND: str
    UPGRADE: str
    PERCENT: str


@dataclass(frozen=True)
class CharacterScheme(ColorScheme):
    PRIMARY: str
    OUTLINE: str
    BACKGROUND: str
    BACKGROUND_2: str
    STAT_PRIMARY: str
    STATPOINTS: str
    STATBUTTON: str
    STATBUTTON_DISABLED: str
    UPGRADE: str
    UPGRADE_BACKGROUND: str
    TIERLIST: str

    def get_row_name_color(self, key: str | int) -> str:
        if key == 'rank' or isinstance(key, int) and key > 100:
            return self.TIERLIST

        return self.PRIMARY


DEFAULT_SCHEME = ColorScheme(
    ELO="#D702EB",
    PRESTIGE="#EAB379",
    FACTIONS=("#3A8BD9", "#C32929"),
    CLASSES=("#C7966F", "#189DE1", "#98CE64", "#4F72D4"),
    ITEM_QUALITY=("#3E4853", "#34CB49", "#0681EA", "#8E27ED", "#D88900", "#F93030"),
    STAT_QUALITY=("#FFFFFF", "#34CB49", "#0681EA", "#8E27ED", "#D88900", "#F93030"),
    TIERLIST_RANK=(
        '#AE0A8B',
        '#C646A0',
        '#9F46C6',
        '#5A46C6',
        '#467BC6',
        '#46C0C6',
        '#46C695',
        '#46C661',
        '#81C646',
        '#B8C646',
        '#C6BA46',
        '#C69346',
        '#C67546',
        '#C66446',
        '#C65746',
        '#B91515',
        '#740000',
    ),
)

DEFAULT_ITEM_SCHEME = ItemScheme(
    **asdict(DEFAULT_SCHEME),
    BACKGROUND="#10131D",
    ID="#3E4853",
    GS="#34CB49",
    BOUND="#34CB49",
    UPGRADE="#F5C247",
    PERCENT="#FFFFFF",
)

DEFAULT_CHARACTER_SCHEME = CharacterScheme(
    **asdict(DEFAULT_SCHEME),
    PRIMARY='#FFFFFF',
    OUTLINE='#000000',
    BACKGROUND='#181d24',
    BACKGROUND_2='#12151e',
    STAT_PRIMARY='#f5c247',
    STATPOINTS='#34cb49',
    STATBUTTON='#34cb49',
    STATBUTTON_DISABLED='#5b858e',
    UPGRADE='#dae8ea',
    UPGRADE_BACKGROUND='#10131dcc',
    TIERLIST='#1bffec',
)


def get_quality(percent: int | float, *, extended: bool = False) -> int:
    if percent >= 110 and extended:
        return 5
    elif percent >= 99 and extended:
        return 4
    elif percent >= 90:
        return 3
    elif percent >= 70:
        return 2
    elif percent >= 50:
        return 1

    return 0
