from __future__ import annotations

import math
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, AnyStr, Mapping, Optional, Sequence, TypedDict, TypeVar, Union

from PIL import Image, ImageDraw, ImageFont

from ..utils import math_round
from .colors import DEFAULT_PALLETE, ColorPallete, get_quality
from .formatters import format_bigint, format_stat
from .strings import BOUND_NAMES, QUALITY_NAMES, get_item_name, get_stat_name

if TYPE_CHECKING:
    from typing_extensions import Unpack

    from ..item import Item
    from ..types.item import BoundId, ItemStatDict

    Coords = Union[Sequence[float], Sequence[Sequence[float]]]
    T = TypeVar('T', int, float, tuple[float, float], tuple[int, int], list[int], Coords)

    _Ink = Union[float, tuple[int, ...], str]

    class _RenderProps(TypedDict):
        name: str
        id: Optional[int]
        type: str
        percent: int
        tier: int
        upgrade: Optional[int]
        stacks: Optional[int]
        gearscore: int
        bound: BoundId
        stats: tuple[ItemStatDict, ...]


__all__ = ('Viewgear',)

IMAGE_SIZE = (244, 224)
ERROR_ITEM: _RenderProps = {
    'name': 'Error: Not Found',
    'id': None,
    'type': 'Error',
    'percent': 0,
    'tier': 0,
    'bound': 0,
    'stats': (),
    'upgrade': 0,
    'stacks': 0,
    'gearscore': 0,
}


def text_breaker(
    text: str,
    text_width: int,
    text_height: int,
    text_fontsize: int,
    font: ImageFont.FreeTypeFont,
    size_coefficent: int = 1,
) -> tuple[str, int]:
    font = font.font_variant(size=text_fontsize)

    text_size = font.getbbox(str(text))
    lines: list[str] = []
    if text_size[2] >= text_width:
        text_final = ""
        text_line = ""
        words = text.split()
        for i, word in enumerate(words):
            if font.getlength(text_line + word) >= text_width and i != 0:
                lines.append(text_line)
                text_line = ""
                text_final += "\n"
            text_line += f"{word} "
            text_final += f"{word} "
        lines.append(text_line)
    else:
        text_final = text
    text_alllines_height = 0
    for line in lines:
        text_alllines_height += (font.getbbox(line))[3]
    if text_alllines_height >= text_height and text_fontsize > 8 or len(lines) == 1 and text_size[2] >= text_width:
        edited_font_size = text_fontsize - 2 * size_coefficent
        text_final, text_fontsize = text_breaker(
            text,
            text_width,
            text_height,
            edited_font_size - 1,
            font,
            size_coefficent,
        )
    return text_final, text_fontsize


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
    def __init__(self, im: Image.Image, mode: Union[str, None] = None, size_multiplier: int = 1):
        self._draw = ImageDraw.Draw(im, mode)
        self.size_multiplier = size_multiplier

    def _getsize(self, data: T) -> T:
        return get_size(data, self.size_multiplier)

    def _getfont(self, font: ImageFont.FreeTypeFont | None) -> ImageFont.FreeTypeFont | None:
        if font:
            return font.font_variant(size=font.size * self.size_multiplier)
        return font

    def text(
        self,
        xy: tuple[float, float],
        text: AnyStr,
        fill: _Ink | None = None,
        font: ImageFont.FreeTypeFont | None = None,
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
    ):
        return self._draw.text(
            xy=self._getsize(xy),
            text=text,
            fill=fill,
            font=self._getfont(font),
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
        font: ImageFont.FreeTypeFont | None = None,
        direction: str | None = None,
        features: list[str] | None = None,
        language: str | None = None,
        embedded_color: bool = False,
        *,
        font_size: float | None = None,
    ):
        return self._draw.textlength(
            text=text,
            font=font,
            direction=direction,
            features=features,
            language=language,
            embedded_color=embedded_color,
            font_size=font_size,
        )

    def rectangle(self, xy: Coords, fill: _Ink | None = None, outline: _Ink | None = None, width: int = 1):
        return self._draw.rectangle(xy=self._getsize(xy), fill=fill, outline=outline, width=self._getsize(width))


class Viewgear:
    def __init__(
        self,
        loc: Mapping[str, Any],
        pallete: ColorPallete = DEFAULT_PALLETE,
        size_multiplier: int = 1,
    ):
        self.loc = loc
        self.pallete = pallete
        self.size_multiplier = size_multiplier

        self.fonts = self._init_fonts()

    def _init_fonts(self) -> dict[int, dict[int, ImageFont.FreeTypeFont]]:
        bold = ImageFont.truetype(Path(__file__).parent / 'assets/fonts/bold.ttf')
        semibold = ImageFont.truetype(Path(__file__).parent / 'assets/fonts/semibold.ttf')

        return {
            400: {
                13: semibold.font_variant(size=13),
                16: semibold.font_variant(size=16),
            },
            600: {
                15: bold.font_variant(size=15),
                20: bold.font_variant(size=20),
            },
        }

    def _get_display_items(self, *items: Item) -> tuple[Item, ...]:
        item_count = len(items)

        charms = [item for item in items if item.type == 'charm']
        charm_count = len(charms)

        if item_count == charm_count:
            return tuple(charms)

        return tuple(item for item in items if item.type != 'charm')

    def _get_grid_size(self, item_amount: int) -> tuple[int, int]:
        root = math.sqrt(item_amount)

        width = max(math.ceil(root), 1)
        height = max(math_round(root), 1)

        return (width, height)

    def _get_background_size(self, grid_size: tuple[int, int], *, text_bg_height: int, margin: int) -> tuple[int, int]:
        width = (IMAGE_SIZE[0] * grid_size[0]) + ((grid_size[0] - 1) * margin)
        height = (IMAGE_SIZE[1] * grid_size[1]) + ((grid_size[1] - 1) * margin + text_bg_height)

        return (width, height)

    def _get_item_positions(self, grid_size: tuple[int, int], *, text_bg_height: int, margin: int) -> list[tuple[int, int]]:
        item_positions: list[tuple[int, int]] = []

        for grid_y in range(grid_size[1]):
            for grid_x in range(grid_size[0]):
                x_position = (IMAGE_SIZE[0] + margin) * grid_x
                y_position = (IMAGE_SIZE[1] + margin) * grid_y + text_bg_height

                item_positions.append((x_position, y_position))

        return item_positions

    def _draw_text(self, text: str) -> None: ...

    @contextmanager
    def _render_single(self, **item: Unpack[_RenderProps]):
        quality = get_quality(item['percent'])

        border_color = self.pallete.quality[quality]
        border_width = 3

        with Image.new('RGB', get_size(IMAGE_SIZE, size_multiplier=self.size_multiplier)) as image:
            draw = DrawScaler(image, size_multiplier=self.size_multiplier)

            # Background and borders
            offset = 1 / self.size_multiplier  # Very bad, but I don't see other solution here.
            draw.rectangle(
                ((0, 0), (IMAGE_SIZE[0] - offset, IMAGE_SIZE[1] - offset)),
                fill=self.pallete.viewgear_background,
                outline=border_color,
                width=border_width,
            )

            # Item name + upgrade
            position = (10, 10)
            name_text_width = draw.textlength(item['name'], font=self.fonts[600][20])
            draw.text(position, item['name'], font=self.fonts[600][20], fill=border_color)
            if (
                isinstance(item['upgrade'], int)
                and item['upgrade'] > 0
                or isinstance(item['stacks'], int)
                and item['stacks'] > 0
            ):
                if isinstance(item['upgrade'], int) and item['upgrade'] > 0:
                    upgrade_text = f" +{format_bigint(item['upgrade'], accuracy=0, maxdigit=4)}"
                elif isinstance(item['stacks'], int) and item['stacks'] > 0:
                    upgrade_text = f" x{item['stacks']}"
                else:
                    upgrade_text = ''

                if name_text_width >= (210):
                    position = (22, 30)
                    draw.text(
                        (name_text_width - position[0], position[1]),
                        upgrade_text,
                        font=self.fonts[600][20],
                        fill=self.pallete.upgrade,
                    )
                else:
                    position = (10, 10)
                    draw.text(
                        (name_text_width + position[0], position[1]),
                        upgrade_text,
                        font=self.fonts[600][20],
                        fill=self.pallete.upgrade,
                    )

            # Item Rarity, Type, Percent
            position = (10, 36)
            draw.text(
                position,
                f"{QUALITY_NAMES[quality].title()} T{item['tier']+1} {item['type'].title()} {item['percent']}%",
                font=self.fonts[600][15],
                fill=self.pallete.percent,
            )

            # Item GS
            position = (10, 59)
            if item['gearscore'] > 0:
                draw.text(
                    (position),
                    f"GS: {format_bigint(item['gearscore'], accuracy=0, maxdigit=4)}",
                    font=self.fonts[400][13],
                    fill=self.pallete.gs,
                )
                position = position[0] + 50, position[1]

            # Item ID
            id_text = f"ID: {item['id'] or 'Generated'}"
            draw.text(
                (position),
                id_text,
                font=self.fonts[400][13],
                fill=self.pallete.id,
            )

            # Item bound
            id_text_width = draw.textlength(id_text, font=self.fonts[400][13])
            position = (position[0]) + id_text_width, (position[1])
            if item['bound'] > 0:
                draw.text(
                    position,
                    f"  {BOUND_NAMES[item['bound']]}",  # remove spaces
                    font=self.fonts[400][13],
                    fill=self.pallete.bound,
                )

            # Stats
            stats = item['stats']
            position = 10, 78
            for stat in stats:
                formatted = format_stat(stat['id'], stat['value'], 1, 5)
                if stat['type'] == 'main':
                    text = f"{formatted} {get_stat_name(self.loc,stat['id'])}"
                    fill = border_color
                elif stat['type'] == 'sub':
                    text = f"+ {formatted} {get_stat_name(self.loc,stat['id'])} {stat['percent']}%"
                    fill = self.pallete.stat_quality[get_quality(stat['percent'])]
                else:
                    continue

                draw.text((position), text, font=self.fonts[400][16], fill=fill)
                position = position[0], position[1] + 20

            yield image

    @contextmanager
    def render(
        self,
        *items: Item,
        text: Optional[str] = None,
        text_color_id: Optional[int] = None,
    ):
        display_items = self._get_display_items(*items)

        text_bg_height = 120 if text else 0
        margin = 5
        grid_size = self._get_grid_size(len(display_items))

        background_size = self._get_background_size(grid_size, text_bg_height=text_bg_height, margin=margin)
        item_positions = self._get_item_positions(grid_size, text_bg_height=text_bg_height, margin=margin)

        text_bg_width = background_size[0]
        text_color = self.pallete.classes[text_color_id] if text_color_id else (255, 255, 255)

        with Image.new(
            'RGB',
            get_size(background_size, size_multiplier=self.size_multiplier),
            self.pallete.viewgear_background,
        ) as background:
            if text is not None:
                text, text_size = text_breaker(
                    text,
                    text_bg_width,
                    text_bg_height,
                    text_fontsize=(43),
                    font=self.fonts[400][(43)],
                    size_coefficent=self.size_multiplier,
                )

                draw = DrawScaler(background, size_multiplier=self.size_multiplier)
                draw.text(
                    (text_bg_width / 2, text_bg_height / 2),
                    text,
                    font=self.fonts[400],
                    font_size=text_size,
                    anchor="mm",
                    fill=text_color,
                )

            for index, item in enumerate(display_items):
                with self._render_single(
                    name=get_item_name(self.loc, item.type, item.tier),
                    id=item.id,
                    type=item.type,
                    percent=item.percent,
                    tier=item.tier,
                    upgrade=item.upgrade,
                    stacks=item.stacks,
                    gearscore=item.gearscore,
                    bound=item.bound,
                    stats=item.stats.to_raw(),
                ) as single:
                    background.paste(single, get_size(item_positions[index], self.size_multiplier))

            if len(display_items) == 0:
                with self._render_single(**ERROR_ITEM) as image:
                    background.paste(image, get_size(item_positions[0], self.size_multiplier))

            yield background
