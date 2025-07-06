from __future__ import annotations


def format_bigint(number: float, accuracy: int = 2, maxdigit: int = 5) -> str:
    """Formats `number` to scientific notation conditionally.

    Parameters
    ----------
    number : int | float
        Number to format.
    accuracy : int, optional
        Amount of digits after the dot in scientific notation. Defaults to 2.
    maxdigit : int, optional
        Maximum number of digits before converting to scientific notation. Defaults to 5.

    Returns
    -------
    str
        String representing the number in normal or scientific notation.
    """

    if len(str(int(number))) > maxdigit:
        return f"{number:.{accuracy}e}"
    else:
        return f"{number}"


# TODO: Test if defining this in function will be faster than global scope lookup
STAT_FORMAT_TYPES = {8: 1, 9: 1, 13: 2, 14: 2, 16: 2, 18: 3, 101: 4, 102: 4, 103: 4, 104: 5, 105: 5, 106: 5, 107: 5}


def format_stat(id: int, value: float, accuracy: int = 2, maxdigit: int = 5) -> str:
    type = STAT_FORMAT_TYPES[id] if id in STAT_FORMAT_TYPES else 0

    if type == 1:
        return f'{format_bigint(round(value/10, 1), accuracy, maxdigit)}'
    elif type == 2:
        return f'{format_bigint(round(value/10, 1), accuracy, maxdigit)}%'
    elif type == 3:
        return f'{format_bigint(value, accuracy, maxdigit)}%'
    elif type == 4:
        return f'{format_bigint(round(value), accuracy, maxdigit)}'
    elif type == 5:
        return f'{format_bigint(round(value, 2), accuracy, maxdigit)}'

    return format_bigint(value, accuracy, maxdigit)
