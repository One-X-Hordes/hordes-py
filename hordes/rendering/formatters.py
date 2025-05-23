from __future__ import annotations


def format_bigint(number: float, accuracy: int = 2, maxdigit: int = 5) -> str:
    """Formats `number` to scientific notation conditionally

    :param number: Number to format
    :type number: int | float
    :param accuracy: Amount of digits after dot in scientific notation, defaults to 2
    :type accuracy: int, optional
    :param maxdigit: Maximum amount of digits before number converted to scientific notation, defaults to 5
    :type maxdigit: int, optional
    :return: String representing number in normal or scientific notation
    :rtype: str
    """

    if len(str(int(number))) > maxdigit:
        return f"{number:.{accuracy}e}"
    else:
        return f"{number}"


# TODO: Test if defining this in function will be faster than global scope lookup
STAT_FORMATS = {8: 1, 9: 1, 13: 2, 14: 2, 16: 2, 18: 3, 34: 4, 35: 4, 36: 4, 37: 5, 38: 5, 39: 5, 40: 5}


def format_stat(id: int, value: float, accuracy: int = 2, maxdigit: int = 5) -> str:
    type = STAT_FORMATS[id] if id in STAT_FORMATS else 0

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
