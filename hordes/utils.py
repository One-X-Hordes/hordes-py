import math
from decimal import Decimal
from typing import Any, Callable, Iterable, Literal, Union, overload

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


@overload
def math_round(x: float, ndigits: Literal[0] = 0) -> int:
    """Always rounds `x < .5` down and `x >= 0.5` up.

    Parameters
    ----------
    x : float
        Number to round.

    Returns
    -------
    int
        Rounded number.
    """


@overload
def math_round(x: float, ndigits: int) -> float:
    """Always rounds `x < .5` down and `x >= 0.5` up.

    Parameters
    ----------
    x : float
        Number to round.

    Returns
    -------
    float
        Rounded number.
    """


def math_round(x: float, ndigits: int = 0) -> float:
    upscaled: float = x * 10**ndigits

    floor_x = math.floor(upscaled)

    if (upscaled - floor_x) < 0.5:
        rounded = floor_x
    else:
        rounded = math.ceil(upscaled)

    downscaled = rounded / 10**ndigits

    return int(downscaled) if ndigits == 0 else downscaled


def find_first_index(
    iterable: Iterable[float],
    value: float,
    comp_func: Callable[[float, float], bool] = lambda a, b: a >= b,
) -> int:
    """
    Returns the index of the first element in the iterable that satisfies the comparison function.

    Parameters
    ----------
    iterable : Iterable[float]
        An iterable of float values to search through.
    value : float
        The reference value to compare against each element of the iterable.
    comp_func : Callable[[float, float], bool], optional
        A binary comparison function that takes two floats and returns a boolean.
        Defaults to checking if `value >= element`.

    Returns
    -------
    int
        The index of the first element in the iterable for which `comp_func(value, element)`
        returns True.

    Raises
    ------
    IndexError
        If no element satisfies the comparison function.

    Examples
    --------
    >>> find_first_index([1.0, 2.5, 3.0], 2.0)
    1
    >>> find_first_index([5.0, 3.0, 1.0], 2.0, lambda a, b: a < b)
    2
    >>> find_first_index([1.0, 2.0, 3.0], 0.5)
    Traceback (most recent call last):
        ...
    IndexError: No matching element found
    """

    for i, iv in enumerate(iterable):
        if comp_func(value, iv):
            return i

    raise IndexError("No matching element found")


def get_attr_or_item(obj: Any, name: Union[str, int]) -> Any:
    """
    Retrieve an attribute or item from an object.

    Parameters
    ----------
    obj : Any
        The object to retrieve from.
    name : Union[str, int]
        The attribute name or item key/index.

    Returns
    -------
    Any
        The value of the attribute or item retrieved.

    Raises
    ------
    AttributeError
        If attribute access fails and item access is not attempted or fails.
    KeyError, IndexError, TypeError
        If item access fails.
    """

    if isinstance(name, str):
        try:
            return getattr(obj, name)
        except AttributeError:
            pass

    try:
        return obj[name]
    except Exception as error:
        raise type(error)(f"Failed to get attribute or item '{name}': {error}") from error


def multiply(x0: float, x1: float) -> float:
    """Safe float multiplication to prevent floating point rounding errors.

    Parameters
    ----------
    x0 : float
    x1 : float

    Returns
    -------
    float
        Multiplied float
    """
    return float(Decimal(str(x0)) * Decimal(str(x1)))
