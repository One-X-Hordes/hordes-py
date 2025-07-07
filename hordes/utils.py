import math
from typing import Any, Iterable, Union

# fmt: off
__all__ = (
    'MISSING',
)
# fmt: on


class _MissingSentinel:
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __hash__(self) -> int:
        return 0

    def __repr__(self):
        return '...'


MISSING: Any = _MissingSentinel()


def math_round(x: Union[int, float]) -> int:
    """Always rounds `x < .5` down and `x >= 0.5` up.

    Parameters
    ----------
    x : int | float
        Number to round.

    Returns
    -------
    int
        Rounded number.
    """

    floor_x = math.floor(x)

    if (x - floor_x) < 0.5:
        return floor_x
    else:
        return math.ceil(x)


def iter_index(iterable: Iterable[float], value: float) -> int:
    """

    Parameters
    ----------
    iterable : Iterable[float]
    value : float

    Returns
    -------
    int
        Index of iterable where `value` >= `iterable[index]` if exists. Otherwise -1.
    """

    for i, iv in enumerate(iterable):
        if value >= iv:
            return i

    return -1
