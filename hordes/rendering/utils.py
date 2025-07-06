from __future__ import annotations

from typing import TYPE_CHECKING, Any, AnyStr, Sequence, TypeVar, Union

from PIL import Image, ImageDraw, ImageFont

from .font import FontLoaderP

if TYPE_CHECKING:

    Coords = Union[Sequence[float], Sequence[Sequence[float]]]
    T = TypeVar('T', int, float, tuple[float, float], tuple[int, int], list[int], Coords)

    _Ink = Union[float, tuple[int, ...], str]


def set_opacity(image: Image.Image, opacity: float) -> Image.Image:
    """Multiplies by `opacity` value of each alpha channel point.

    Parameters
    ----------
    image : Image.Image
        Original image to edit.
    opacity : float
        Opacity multiplier.

    Returns
    -------
    Image.Image
        New image with changed alpha channel.
    """

    r, g, b, a = image.split()
    a = a.point(lambda p: int(p * opacity))  # pyright: ignore[reportUnknownMemberType]
    return Image.merge("RGBA", (r, g, b, a))


def resize(image: Image.Image, wh: tuple[int, int]) -> Image.Image:
    """Resizes image in place using Lanczos method.

    Parameters
    ----------
    image : Image.Image
        Original image to edit.
    wh : tuple[int, int]
        Resulting size.

    Returns
    -------
    Image.Image
        Inserted image to allow chaining.
    """

    image.thumbnail(wh, Image.Resampling.LANCZOS)
    return image


def account_draw_offset(coords: Coords) -> Coords:
    if isinstance(coords[0], Sequence) and isinstance(coords[1], Sequence):
        return coords[0], (coords[1][0] - 1, coords[1][1] - 1)

    elif (
        isinstance(coords[0], (int, float))
        and isinstance(coords[1], (int, float))
        and isinstance(coords[2], (int, float))  # Is there a better way to shut up type checker?
        and isinstance(coords[3], (int, float))
    ):
        return coords[0], coords[1], float(coords[2] - 1), float(coords[3] - 1)

    raise ValueError


def get_size(data: T, size_multiplier: int) -> T:
    if isinstance(data, (int, float)):
        return data * size_multiplier
    elif isinstance(data, tuple):
        return tuple(get_size(size, size_multiplier) for size in data)  # type: ignore
    elif isinstance(data, Sequence):
        return [get_size(size, size_multiplier) for size in data]  # type: ignore
    else:
        raise TypeError(f'Expected int, float, tuple or list, received {data.__class__.__name__}')


class DrawScaler:
    def __init__(self, im: Image.Image, font_loader: FontLoaderP, mode: Union[str, None] = None, size_multiplier: int = 1):
        self._draw = ImageDraw.Draw(im, mode)
        self.font_loader = font_loader
        self.size_multiplier = size_multiplier

    def _getsize(self, data: T) -> T:
        return get_size(data, self.size_multiplier)

    def _getfont(self, weight: int, size: float) -> ImageFont.FreeTypeFont:
        return self.font_loader.get_font(weight, size=size * self.size_multiplier)

    def text(
        self,
        xy: tuple[float, float],
        text: AnyStr,
        fill: _Ink | None = None,
        font_size: float = 16,
        font_weight: int = 400,
        anchor: str | None = None,
        spacing: float = 4,
        align: str = "left",
        direction: str | None = None,
        features: list[str] | None = None,
        language: str | None = None,
        stroke_width: float = 0,
        stroke_fill: _Ink | None = None,
        embedded_color: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        return self._draw.text(
            xy=self._getsize(xy),
            text=text,
            fill=fill,
            font=self._getfont(font_weight, font_size),
            anchor=anchor,
            spacing=spacing,
            align=align,
            direction=direction,
            features=features,
            language=language,
            stroke_width=self._getsize(stroke_width),
            stroke_fill=stroke_fill,
            embedded_color=embedded_color,
            *args,
            **kwargs,
        )

    def textlength(
        self,
        text: AnyStr,
        font_size: float = 16,
        font_weight: int = 400,
        direction: str | None = None,
        features: list[str] | None = None,
        language: str | None = None,
        embedded_color: bool = False,
    ) -> float:
        return self._draw.textlength(
            text=text,
            font=self.font_loader.get_font(font_weight, font_size),
            direction=direction,
            features=features,
            language=language,
            embedded_color=embedded_color,
            font_size=font_size,
        )

    def textbbox(
        self,
        xy: tuple[float, float],
        text: AnyStr,
        font_size: float = 16,
        font_weight: int = 400,
        anchor: str | None = None,
        spacing: float = 4,
        align: str = "left",
        direction: str | None = None,
        features: list[str] | None = None,
        language: str | None = None,
        stroke_width: float = 0,
        embedded_color: bool = False,
    ) -> tuple[float, float, float, float]:
        return self._draw.textbbox(
            xy=xy,
            text=text,
            font=self.font_loader.get_font(font_weight, font_size),
            anchor=anchor,
            spacing=spacing,
            align=align,
            direction=direction,
            features=features,
            language=language,
            stroke_width=stroke_width,
            embedded_color=embedded_color,
            font_size=font_size,
        )

    def rectangle(
        self,
        xy: Coords,
        fill: _Ink | None = None,
        outline: _Ink | None = None,
        width: int = 1,
    ) -> None:
        return self._draw.rectangle(
            xy=account_draw_offset(self._getsize(xy)),
            fill=fill,
            outline=outline,
            width=self._getsize(width),
        )

    def rounded_rectangle(
        self,
        xy: Coords,
        radius: float = 0,
        fill: _Ink | None = None,
        outline: _Ink | None = None,
        width: int = 1,
        *,
        corners: tuple[bool, bool, bool, bool] | None = None,
    ) -> None:
        return self._draw.rounded_rectangle(
            xy=account_draw_offset(self._getsize(xy)),
            radius=radius,
            fill=fill,
            outline=outline,
            width=width,
            corners=corners,
        )
