from io import BytesIO
from itertools import chain
from typing import Any, Mapping, Optional

from PIL import Image, ImageOps

from ..character import Character
from ..data import EQUIP_SLOT_IDS
from ..item import Item
from ..models import Ranking
from ..tierlist import get_leaderboard_rank, get_tierlist_rank
from ..utils import math_round
from .assets import AssetLoaderP
from .colors import DEFAULT_CHARACTER_SCHEME, CharacterScheme, get_quality
from .font import FontLoaderP
from .formatters import format_bigint, format_stat
from .layout import Gap, Grid, GridColumns, Indentation, Layout, Panel, Rectangle, create_panels, pad_bbox
from .strings import (
    get_charpanel_keys,
    get_class_name,
    get_faction_name,
    get_row_name,
    get_stat_name,
    get_tierlist_rank_name,
)
from .utils import DrawScaler, resize, set_opacity

# fmt: off
__all__ = (
    'CharacterImage',
)
# fmt: on

StatLayout = tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]


DEFAULT_STAT_LAYOUT: StatLayout = (
    (6, 8, 7, 9, 12, 13),
    (10, 11, 17, 14, 16),
    (15, 19, 18, 25, 26),
)

BUILDSCORE_STAT_LAYOUT: StatLayout = (
    (6, 8, 7, 9, 12, 13),
    (10, 11, 17, 14, 16),
    (103, 101, 102, 18, 25, 107),
)


def get_item_image_path(item: Item, quality: int) -> str:
    return f'items/{item.type}/{item.type}{item.tier}_q{quality}'


def get_slot_image_path(slot: int) -> str:
    return f'ui/slotbg/{slot}'


def get_prestige_string(character: Character, loc: Mapping[str, Any]) -> str:
    requirement = min(character.prestige.rank + 1, 12) * 4
    return f"{character.prestige.value:,} / {requirement}k ({loc['ui']['charpanel']['rank']} {character.prestige.rank}/12)"


class CharacterLayout(Layout):
    def __init__(self, font_loader: FontLoaderP):
        font_large = font_loader.get_font(400, 15)
        font_small = font_loader.get_font(400, 13)

        font_large_line_height = sum(font_large.getmetrics())
        font_small_line_height = sum(font_small.getmetrics())

        panel_padding = Indentation(4)
        panel_gap = Gap(0, 3)
        gap = Gap(4)

        self.title = Panel(
            height=math_round(font_large.size * 1.15 + 3 * 2),
            padding=Indentation(8, 0, 8, 4),
        )
        self.char_data = Grid(
            *create_panels(14, height=font_large_line_height),
            padding=panel_padding,
            gap=panel_gap,
            columns=GridColumns(1, 2),
        )
        self.statpoints = Grid(
            *chain(
                *(
                    (
                        Panel(height=font_large_line_height),
                        Panel(),
                        Panel(width=17, height=17),
                    )
                    for _ in range(7)
                )
            ),
            padding=panel_padding,
            gap=panel_gap,
            columns=GridColumns(1, 1, 'auto'),
            align='center',
        )
        item_amount = 11
        self.items = Grid(
            *create_panels(item_amount, width=40, height=40, border=Indentation(3)),
            gap=gap,
            columns=GridColumns(*('auto',) * item_amount),
        )
        self.stats = [
            Grid(
                *create_panels(12, height=font_small_line_height),
                padding=panel_padding,
                gap=panel_gap,
                columns=GridColumns(1, 1),
            )
            for _ in range(3)
        ]

        super().__init__(
            self.title,
            Grid(
                Grid(self.char_data, self.statpoints, columns=GridColumns(3, 2), gap=gap),
                self.items,
                Grid(*self.stats, columns=GridColumns(1, 1, 1), gap=gap),
                gap=gap,
            ),
            padding=Indentation(0, 5, 5),
            outline=1,
        )


class CharacterImage:
    def __init__(
        self,
        background: BytesIO,
        loc: Mapping[str, Any],
        loader: AssetLoaderP,
        font_loader: FontLoaderP,
        color_scheme: CharacterScheme = DEFAULT_CHARACTER_SCHEME,
        ranking: Optional[Ranking] = None,
    ) -> None:
        self.background = background
        self.loader = loader
        self.font_loader = font_loader
        self.loc = loc
        self.color_scheme = color_scheme
        self.ranking = ranking

        self.layout = CharacterLayout(font_loader)

    @staticmethod
    def render_background(
        loc: Mapping[str, Any],
        font_loader: FontLoaderP,
        color_scheme: CharacterScheme = DEFAULT_CHARACTER_SCHEME,
        rank: bool = False,
        buildscore: bool = False,
    ) -> BytesIO:
        layout = CharacterLayout(font_loader)

        width, height = layout.outer_box.width, layout.outer_box.height

        with Image.new('RGBA', (width, height)) as image:
            draw = DrawScaler(image, font_loader=font_loader)

            draw.rectangle(
                layout.outer_box.bbox,
                fill=color_scheme.BACKGROUND,
                outline=color_scheme.OUTLINE,
                width=layout.outline,
            )

            draw.rectangle(
                layout.char_data.outer_box.bbox,
                fill=color_scheme.BACKGROUND_2,
            )

            draw.rectangle(
                layout.statpoints.outer_box.bbox,
                fill=color_scheme.BACKGROUND_2,
            )

            for panel in layout.stats:
                draw.rectangle(
                    panel.outer_box.bbox,
                    fill=color_scheme.BACKGROUND_2,
                )

            draw.text(
                (layout.title.inner_box.top_left[0], layout.title.inner_box.center[1]),
                loc['ui']['headers']['character'],
                fill=color_scheme.PRIMARY,
                font_weight=700,
                font_size=17,
                anchor='lm',
            )

            for i, element in enumerate(get_charpanel_keys(rank=rank)):
                draw.text(
                    layout.char_data.rows[i][0].inner_box.top_left,
                    get_row_name(loc, element),
                    fill=color_scheme.get_row_name_color(element),
                    font_weight=400,
                    font_size=15,
                )

            for i, id in enumerate(list(range(6)) + [22]):
                draw.text(
                    layout.statpoints.rows[i][0].inner_box.top_left,
                    get_stat_name(loc, id),
                    fill=color_scheme.get_row_name_color(id),
                    font_weight=400,
                    font_size=15,
                )

            stat_layout = BUILDSCORE_STAT_LAYOUT if buildscore else DEFAULT_STAT_LAYOUT
            for c, column in enumerate(stat_layout):
                for r, row in enumerate(column):
                    draw.text(
                        layout.stats[c].rows[r][0].inner_box.top_left,
                        get_stat_name(loc, row),
                        fill=color_scheme.get_row_name_color(row),
                        font_weight=400,
                        font_size=13,
                    )

            bytes_ = BytesIO()
            image.save(bytes_, format="PNG")
            bytes_.seek(0)

        return bytes_

    def render(
        self,
        character: Character,
        rank: bool = False,
        buildscore: bool = False,
        extended_quality: bool = False,
    ) -> BytesIO:
        with Image.open(self.background) as image:
            draw = DrawScaler(image, font_loader=self.font_loader)

            stats = character.stats
            statpoints = character.statpoints

            class_name = get_class_name(self.loc, character.class_id)
            faction_name = get_faction_name(self.loc, character.faction_id)

            # Items
            for slot, item in character.slots:
                if slot not in EQUIP_SLOT_IDS:
                    continue

                if item:
                    quality = get_quality(item.percent, extended=extended_quality)
                    image_path = get_item_image_path(item, quality)
                    border_color = self.color_scheme.ITEM_QUALITY[quality]
                else:
                    image_path = get_slot_image_path(slot)
                    border_color = '#293c40'

                element = self.layout.items.children[slot - 101]
                position = element.outer_box.top_left
                border = element.border
                border_size = (int(border.top), int(border.right), int(border.bottom), int(border.left))

                with Image.open(self.loader.open(image_path)) as img_:
                    with ImageOps.expand(img_, border=border_size, fill=border_color) as img:
                        image.paste(img, position)

                if item and item.type != 'charm' and item.upgrade and item.upgrade > 0:
                    text_position = element.inner_box.shift_position(-4, -4).bottom_right
                    text = f"+{format_bigint(item.upgrade, accuracy=0, maxdigit=2)}"

                    bbox = draw.textbbox(
                        text_position,
                        text,
                        font_weight=700,
                        font_size=13,
                        anchor='rb',
                    )

                    draw.rounded_rectangle(
                        pad_bbox(bbox, Indentation(1)),
                        radius=2,
                        fill=self.color_scheme.UPGRADE_BACKGROUND,
                    )

                    draw.text(
                        text_position,
                        text,
                        fill=self.color_scheme.UPGRADE,
                        font_weight=700,
                        font_size=13,
                        anchor='rb',
                    )

            # Buffs
            icon_size = (30, 30)
            base_position = Rectangle(
                min(
                    self.layout.title.inner_box.width * 0.59,
                    self.layout.title.inner_box.top_right[0] - icon_size[0] * len(character.effects),
                ),
                self.layout.inner_box.top_left[1],
                *icon_size,
            ).shift_position(0, 5)
            for i, effect in enumerate(character.effects):
                if not effect.logic.icon:
                    continue
                buff_img = resize(Image.open(self.loader.open(effect.logic.icon)), icon_size)
                position = base_position.shift_position(buff_img.width * i, 0)
                image.paste(buff_img, position.top_left)

                text_position = position.shift_position(-2, -1).bottom_right
                text = str(effect.level)

                bbox = draw.textbbox(
                    text_position,
                    text,
                    font_weight=700,
                    font_size=12,
                    anchor='rb',
                )

                draw.rounded_rectangle(
                    pad_bbox(bbox, Indentation(1)),
                    radius=2,
                    fill=self.color_scheme.UPGRADE_BACKGROUND,
                )

                draw.text(
                    text_position,
                    text,
                    fill=self.color_scheme.UPGRADE,
                    anchor='rb',
                    font_weight=700,
                    font_size=12,
                )

            # Character data
            data = (
                character.name,
                character.level,
                class_name.title(),
                faction_name.title(),
                get_prestige_string(character, self.loc),
                f'{character.elo.value:,}',
            )
            data_fill = (
                None,
                None,
                self.color_scheme.CLASSES[character.class_id],
                self.color_scheme.FACTIONS[character.faction_id],
                self.color_scheme.PRESTIGE,
                self.color_scheme.ELO,
            )

            with (
                Image.open(self.loader.open(f'ui/classes/{character.class_id}')) as class_img,
                Image.open(self.loader.open(f'ui/factions/{character.faction_id}')) as faction_img,
                Image.open(self.loader.open(f'ui/currency/prestige')) as prestige_img,
                Image.open(self.loader.open(f'ui/elo/{character.elo.rank}')) as elo_img,
            ):
                resize(class_img, (15, 15))
                resize(faction_img, (15, 15))
                resize(prestige_img, (13, 15))
                resize(elo_img, (14, 17))
                data_icon = (
                    None,
                    None,
                    class_img,
                    faction_img,
                    prestige_img,
                    elo_img,
                )

            for id, (stat, fill, icon) in enumerate(zip(data, data_fill, data_icon)):
                position = self.layout.char_data.rows[id][1].inner_box.top_left
                if icon:
                    image.paste(icon, (position[0], position[1] + 2), icon)
                    position = position[0] + icon.width + 3, position[1]
                draw.text(position, str(stat), font_weight=700, font_size=15, fill=fill)

            # Ranks
            if self.ranking and rank:
                rank_id = get_tierlist_rank(self.ranking, stats[107])
                text = get_tierlist_rank_name(rank_id)
                if rank_id in range(2):
                    leaderboard_position = get_leaderboard_rank(self.ranking, stats[107])
                    text = f'#{leaderboard_position + 1} {text}'

                draw.text(
                    self.layout.char_data.rows[-1][1].inner_box.top_left,
                    text,
                    font_weight=700,
                    font_size=15,
                    fill=self.color_scheme.TIERLIST_RANK[rank_id],
                )

            # Statpoints
            arrow = Image.open(self.loader.open('ui/icons/arrow'))
            resize(arrow, (17, 17))

            if not character.statpoints_available:
                background_fill = self.color_scheme.STATBUTTON_DISABLED
            else:
                background_fill = self.color_scheme.STATBUTTON

            arrow_rectangle = Image.new('RGBA', arrow.size, background_fill)
            arrow_rectangle.paste(arrow, mask=arrow)
            if not character.statpoints_available:
                arrow_rectangle = set_opacity(arrow_rectangle, 0.5)

            for i, (id, stat) in enumerate(chain(statpoints, [(22, stats[22])])):
                text = format_stat(id, stats[id], accuracy=2, maxdigit=5)

                if id != 22:
                    arrow_pos = self.layout.statpoints.rows[i][2].inner_box.top_left
                    image.paste(arrow_rectangle, (arrow_pos), arrow_rectangle)
                    if stat:
                        text = f'(+{stat}) {text}'

                position = self.layout.statpoints.rows[i][1].inner_box.top_right
                draw.text(position, text, anchor="ra", font_weight=700, font_size=15, fill=self.color_scheme.STATPOINTS)

            # Stats
            stat_layout = BUILDSCORE_STAT_LAYOUT if buildscore else DEFAULT_STAT_LAYOUT
            for column_index, column in enumerate(stat_layout):
                for row_index, row in enumerate(column):
                    position = self.layout.stats[column_index].rows[row_index][1].inner_box.top_right

                    formatted = format_stat(row, stats[row], 4, 6)
                    draw.text(
                        position,
                        formatted,
                        anchor="ra",
                        font_weight=700,
                        font_size=13,
                        fill=self.color_scheme.STAT_PRIMARY,
                    )

            bytes_ = BytesIO()
            image.save(bytes_, format="PNG")
            bytes_.seek(0)

        return bytes_
