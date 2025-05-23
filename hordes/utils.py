import math
from typing import Any, Union

__all__ = ('MISSING',)


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
    """`Math.round(x)` from javascript.

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
