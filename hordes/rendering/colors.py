from __future__ import annotations

PURPLE_COLOR = (158, 59, 249)
PURPLE_COLOR2 = (142, 39, 237)
BLUE_COLOR = (6, 129, 234)
GREEN_COLOR = (52, 203, 73)
WHITE_COLOR = (255, 255, 255)
GRAY_COLOR = (62, 72, 83)
BLACK_COLOR = (16, 19, 29)
YELLOW_COLOR = (245, 194, 71)
ORANGE_COLOR = (216, 137, 0)
RED_COLOR = (249, 48, 48)


class ColorPallete:
    __slots__ = (
        'elo',
        'prestige',
        'factions',
        'classes',
        'quality',
        'stat_quality',
        'tierlist_rank',
        'viewgear_background',
        'id',
        'gs',
        'bound',
        'upgrade',
        'percent',
    )

    def __init__(self):
        for name in self.__slots__:
            assert hasattr(self, name), f'Attribute \'{name}\' is missing.'


class DefaultPallete(ColorPallete):
    elo = (215, 2, 235)
    prestige = (234, 179, 121)

    factions = ((58, 139, 217), (195, 41, 41))
    classes = ((199, 150, 111), (24, 157, 225), (152, 206, 100), (79, 114, 212))

    _quality_colors = (
        (52, 203, 73),
        (6, 129, 234),
        (142, 39, 237),
        (216, 137, 0),
        (249, 48, 48),
    )

    quality = ((62, 72, 83),) + _quality_colors
    stat_quality = ((255, 255, 255),) + _quality_colors

    tierlist_rank = (
        (116, 0, 0),
        (185, 21, 21),
        (198, 87, 70),
        (198, 100, 70),
        (198, 117, 70),
        (198, 147, 70),
        (198, 186, 70),
        (184, 198, 70),
        (129, 198, 70),
        (70, 198, 97),
        (70, 198, 149),
        (70, 192, 198),
        (70, 123, 198),
        (90, 70, 198),
        (159, 70, 198),
        (198, 70, 160),
        (174, 10, 139),
    )

    viewgear_background = (16, 19, 29)
    id = (62, 72, 83)
    gs = (52, 203, 73)
    bound = (52, 203, 73)
    upgrade = (245, 194, 71)
    percent = (255, 255, 255)


DEFAULT_PALLETE = DefaultPallete()


def get_quality(percent: int, *, extended: bool = True) -> int:
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
