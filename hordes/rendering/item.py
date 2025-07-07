from __future__ import annotations

import math
from io import BytesIO
from typing import TYPE_CHECKING, Any, Mapping, Optional, TypedDict

from PIL import Image

from ..utils import math_round
from .colors import DEFAULT_ITEM_SCHEME, ItemScheme, get_quality
from .font import FontLoaderP
from .formatters import format_bigint, format_stat
from .layout import Indentation, Layout, Panel, create_panels
from .strings import BOUND_NAMES, QUALITY_NAMES, get_item_name, get_stat_name
from .utils import DrawScaler, get_size

if TYPE_CHECKING:
    from typing_extensions import Unpack

    from ..item import Item
    from ..types.item import BoundId, ItemStatDict

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


# fmt: off
__all__ = (
    'ItemImage',
)
# fmt: on

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


def fit_text(
    text: str,
    wh: tuple[int, int],
    font_loader: FontLoaderP,
    font_weight: int,
    font_size: int,
    size_multiplier: int = 1,
) -> tuple[str, int]:
    font = font_loader.get_font(font_weight, font_size * size_multiplier)

    text_bounding_box = font.getbbox(text)

    lines: list[list[str]] = []

    if text_bounding_box[2] >= wh[0]:
        words = text.split()

        line: list[str] = []
        for i, word in enumerate(words):
            if font.getlength(' '.join(line + [word])) >= wh[0] and i != 0:
                lines.append(line)
                line = []

            line.append(word)
        lines.append(line)

        final = '\n'.join([' '.join(line) for line in lines])
    else:
        final = text

    lines_height = sum(font.getbbox(' '.join(line))[3] for line in lines)
    lines_maxwidth = max(font.getlength(' '.join(line)) for line in lines)
    if lines_height >= wh[1] and font_size > 8 or lines_maxwidth >= wh[0]:
        return fit_text(
            text=text,
            wh=wh,
            font_loader=font_loader,
            font_weight=font_weight,
            font_size=font_size - 1,
        )

    return final, font_size * size_multiplier


class ItemLayout(Layout):
    def __init__(self, font_loader: FontLoaderP):
        font_title = font_loader.get_font(700, size=20)
        font_quality = font_loader.get_font(700, size=15)
        font_id = font_loader.get_font(400, size=13)
        font_stats = font_loader.get_font(400, size=16)

        self.title = Panel(height=sum(font_title.getmetrics()))
        self.quality = Panel(height=sum(font_quality.getmetrics()))
        self.id = Panel(height=sum(font_id.getmetrics()), padding=Indentation(4, 0, 3))
        self.stats = Panel(*create_panels(7, height=sum(font_stats.getmetrics())))

        super().__init__(
            Panel(
                self.title,
                self.quality,
                self.id,
                self.stats,
                padding=Indentation(7),
            ),
            width=238,
            height=218,
            border=Indentation(3),
        )


class ItemImage:
    def __init__(
        self,
        loc: Mapping[str, Any],
        font_loader: FontLoaderP,
        color_scheme: ItemScheme = DEFAULT_ITEM_SCHEME,
        error_item: _RenderProps = ERROR_ITEM,
        size_multiplier: int = 1,
    ):
        self.loc = loc
        self.font_loader = font_loader
        self.color_scheme = color_scheme
        self.error_item = error_item
        self.size_multiplier = size_multiplier

        self.layout = ItemLayout(font_loader)

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

    def _get_render_props(self, item: Item) -> _RenderProps:
        return {
            'name': get_item_name(self.loc, item.type, item.tier),
            'id': item.id,
            'type': item.type,
            'percent': item.percent,
            'tier': item.tier,
            'upgrade': item.upgrade,
            'stacks': item.stacks,
            'gearscore': item.gearscore,
            'bound': item.bound,
            'stats': item.stats.to_raw(),
        }

    def _render_single(self, extended_quality: bool = False, **item: Unpack[_RenderProps]):
        quality = get_quality(item['percent'], extended=extended_quality)

        border_color = self.color_scheme.ITEM_QUALITY[quality]
        border_width = 3

        with Image.new('RGB', get_size(IMAGE_SIZE, size_multiplier=self.size_multiplier)) as image:
            draw = DrawScaler(image, font_loader=self.font_loader, size_multiplier=self.size_multiplier)

            # Background and borders
            draw.rectangle(
                self.layout.outer_box.bbox,
                fill=self.color_scheme.BACKGROUND,
                outline=border_color,
                width=border_width,
            )

            # Item name + upgrade
            position = self.layout.title.inner_box.top_left
            draw.text(position, item['name'], font_weight=700, font_size=20, fill=border_color)
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

                text_width = draw.textlength(item['name'], font_weight=700, font_size=20)

                if text_width >= (210):
                    position = (22, 30)
                else:
                    position = (10, 10)

                draw.text(
                    (text_width + position[0], position[1]),
                    upgrade_text,
                    font_weight=700,
                    font_size=20,
                    fill=self.color_scheme.UPGRADE,
                )

            # Item Rarity, Type, Percent
            position = self.layout.quality.inner_box.top_left
            draw.text(
                position,
                f"{QUALITY_NAMES[quality].title()} T{item['tier']+1} {item['type'].title()} {item['percent']}%",
                font_weight=700,
                font_size=15,
                fill=self.color_scheme.PERCENT,
            )

            # Item ID line
            position = self.layout.id.inner_box
            texts = (
                f"GS: {format_bigint(item['gearscore'], accuracy=0, maxdigit=4)}" if item['gearscore'] else None,
                f"ID: {item['id'] or 'Generated'}",
                f"{BOUND_NAMES[item['bound']]}",
            )
            fill = (
                self.color_scheme.GS,
                self.color_scheme.ID,
                self.color_scheme.BOUND,
            )
            gap = 7

            for i, (text, fill) in enumerate(zip(texts, fill)):
                if not text:
                    continue

                draw.text(
                    position.top_left,
                    text=text,
                    fill=fill,
                    font_weight=400,
                    font_size=13,
                )

                length = draw.textlength(
                    text,
                    font_size=13,
                    font_weight=400,
                )

                position = position.shift_position(int(length + gap), 0)

            # Stats
            stats = item['stats']
            for i, stat in enumerate(stats):
                formatted = format_stat(stat['id'], stat['value'], 1, 5)
                if stat['type'] == 'main':
                    text = f"{formatted} {get_stat_name(self.loc,stat['id'])}"
                    fill = border_color
                elif stat['type'] == 'sub':
                    text = f"+ {formatted} {get_stat_name(self.loc,stat['id'])} {stat['percent']}%"
                    fill = self.color_scheme.STAT_QUALITY[get_quality(stat['percent'], extended=extended_quality)]
                else:
                    continue

                position = self.layout.stats.children[i].inner_box.top_left
                draw.text(position, text, font_weight=400, font_size=16, fill=fill)

            return image

    def render(
        self,
        *items: Item,
        text: Optional[str] = None,
        text_color: Optional[str] = None,
        extended_quality: bool = False,
    ):
        display_items = self._get_display_items(*items)

        text_bg_height = 120 if text else 0
        margin = 5
        grid_size = self._get_grid_size(len(display_items))

        background_size = self._get_background_size(grid_size, text_bg_height=text_bg_height, margin=margin)
        item_positions = self._get_item_positions(grid_size, text_bg_height=text_bg_height, margin=margin)

        text_bg_width = background_size[0]

        with Image.new(
            'RGB',
            get_size(background_size, size_multiplier=self.size_multiplier),
            self.color_scheme.BACKGROUND,
        ) as background:
            if text is not None:
                text, text_font_size = fit_text(
                    text,
                    (text_bg_width, text_bg_height),
                    font_loader=self.font_loader,
                    font_weight=400,
                    font_size=43,
                    size_multiplier=self.size_multiplier,
                )

                draw = DrawScaler(background, font_loader=self.font_loader, size_multiplier=self.size_multiplier)
                draw.text(
                    (text_bg_width / 2, text_bg_height / 2),
                    text,
                    font_weight=400,
                    font_size=text_font_size,
                    anchor="mm",
                    align='center',
                    fill=text_color or '#FFF',
                )

            for index, item in enumerate(display_items):
                props = self._get_render_props(item)
                with self._render_single(**props, extended_quality=extended_quality) as single:
                    background.paste(single, get_size(item_positions[index], self.size_multiplier))

            if len(display_items) == 0:
                with self._render_single(**self.error_item) as image:
                    background.paste(image, get_size(item_positions[0], self.size_multiplier))

            bytes_ = BytesIO()
            background.save(bytes_, format="PNG")
            bytes_.seek(0)

        return bytes_
        return bytes_
