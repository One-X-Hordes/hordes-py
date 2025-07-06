from __future__ import annotations

from collections.abc import Sequence
from typing import Iterator, Literal, Optional, SupportsIndex, Union, overload

from ..utils import MISSING

Auto = Literal['auto']
Align = Literal['start', 'center', 'end']


class Indentation:
    def __init__(self, *props: float):
        if len(props) == 1:
            unpacked = (props[0],) * 4
        elif len(props) == 2:
            unpacked = (props[0], props[1]) * 2
        elif len(props) == 3:
            unpacked = (props[0], props[1], props[2], props[1])
        elif len(props) == 4:
            unpacked = props
        else:
            raise ValueError(f'Expected 1-4 props, received {len(props)}')

        self.top, self.right, self.bottom, self.left = unpacked

        self.width = self.left + self.right
        self.height = self.top + self.bottom

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} top={self.top} right={self.right} bottom={self.bottom} left={self.left}>'


class Gap:
    def __init__(self, *props: float):
        if len(props) == 1:
            unpacked = props * 2
        elif len(props) == 2:
            unpacked = props
        else:
            raise ValueError(f'Expected 1-2 props, received {len(props)}')

        self.row, self.column = unpacked

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} row={self.row} column={self.column}>'


class Rectangle:
    def __init__(self, x: float, y: float, w: float, h: float):
        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)

        self.x = x
        self.y = y
        self.top_left = (x, y)
        self.top_right = (x + w, y)
        self.bottom_left = (x, y + h)
        self.bottom_right = (x + w, y + h)
        self.size = (w, h)
        self.width = w
        self.height = h
        self.center = (x + w / 2, y + h / 2)
        self.bbox = (x, y, x + w, y + h)

    def shift_position(self, x: int, y: int):
        new_x = self.x + x
        new_y = self.y + y
        return self.__class__(new_x, new_y, self.width, self.height)

    @classmethod
    def from_bbox(cls, left: float, top: float, right: float, bottom: float):
        width = right - left
        height = bottom - top

        return cls(left, top, width, height)


class Element:
    def __init__(
        self,
        *children: Element,
        width: float = MISSING,
        height: float = MISSING,
        padding: Optional[Indentation] = MISSING,
        border: Optional[Indentation] = MISSING,
        outline: Optional[int] = MISSING,
    ):
        self.children = children
        self.width = width
        self.height = height
        self.padding = padding or Indentation(0)
        self.border = border or Indentation(0)
        self.outline = outline or 0

        self.children_width = max([child._get_width() for child in children] + [0])
        self.children_height = sum([child._get_height() for child in children])

    def _get_width_outer(self) -> float:
        return self.padding.width + self.border.width + self.outline * 2

    def _get_width(self) -> float:
        if self.width is not MISSING:
            return self.width + self._get_width_outer()

        return self.children_width + self._get_width_outer()

    def _get_height_outer(self) -> float:
        return self.padding.height + self.border.height + self.outline * 2

    def _get_height(self) -> float:
        if self.height is not MISSING:
            return self.height + self._get_height_outer()

        return self.children_height + self._get_height_outer()

    def _update(self, x: float, y: float, w: float, h: float) -> None:
        self.inner_box = Rectangle(
            x + self.padding.left + self.border.left + self.outline,
            y + self.padding.top + self.border.top + self.outline,
            w - self._get_width_outer(),
            h - self._get_height_outer(),
        )
        self.outer_box = Rectangle(x, y, w, h)

        self._update_children()

    def _update_children(self) -> None:
        x = self.inner_box.top_left[0]
        y = self.inner_box.top_left[1]
        shift = 0
        for child in self.children:
            if child.width is not MISSING:
                outer_width = child._get_width()
            elif self.width is not MISSING:
                outer_width = self.width
            else:
                outer_width = self.inner_box.width

            outer_height = child._get_height()

            child._update(
                x=x,
                y=y + shift,
                w=outer_width,
                h=outer_height,
            )
            shift += outer_height

    def __iter__(self) -> Iterator[Element]:
        return self.children.__iter__()


class Panel(Element):
    def __init__(
        self,
        *children: Element,
        width: float = MISSING,
        height: float = MISSING,
        padding: Optional[Indentation] = MISSING,
        border: Optional[Indentation] = MISSING,
        outline: Optional[int] = MISSING,
    ):
        super().__init__(*children, width=width, height=height, padding=padding, border=border, outline=outline)


class GridColumns(Sequence[Union[int, Auto]]):
    def __init__(self, *props: int | Auto):
        self.props = props
        self.sum = sum(i for i in props if isinstance(i, int))

    @overload
    def __getitem__(self, key: SupportsIndex) -> int | Auto: ...

    @overload
    def __getitem__(self, key: slice) -> tuple[int | Auto, ...]: ...

    def __getitem__(self, key: Union[slice, SupportsIndex]) -> tuple[int | Auto, ...] | int | Auto:
        return self.props.__getitem__(key)

    def __len__(self) -> int:
        return self.props.__len__()


class Grid(Element):
    def __init__(
        self,
        *children: Element,
        padding: Optional[Indentation] = MISSING,
        border: Optional[Indentation] = MISSING,
        outline: Optional[int] = MISSING,
        gap: Optional[Gap] = MISSING,
        columns: Optional[GridColumns] = MISSING,
        align: Optional[Align] = MISSING,
    ):
        super().__init__(*children, padding=padding, border=border, outline=outline)
        self.gap = gap or Gap(0)
        self.columns = columns or GridColumns(1)
        self.align: Align = align or 'start'

        self.rows: list[list[Element]] = []
        row: list[Element] = []  # This exists to prevent potential unbound error
        for i, child in enumerate(children):
            column_index = i % len(self.columns)
            if column_index == 0:
                row = []
                self.rows.append(row)
            row.append(child)

        widths: list[float] = [0]
        heights: list[float] = [0]
        for row in self.rows:
            width = 0
            height = 0
            auto = 0

            for i, element in zip(self.columns, row):
                if isinstance(i, int):
                    width = max(width, element._get_width() / i)
                else:
                    auto += element._get_width()
                height = max(height, element._get_height())

            widths.append(width * self.columns.sum + auto)
            heights.append(height)

        gaps = self.gap.column * (len(self.columns) - 1)
        self.children_width = max(widths) + gaps
        self.children_height = sum(heights) + (len(self.rows) - 1) * self.gap.row

    def _update_children(self) -> None:
        x = self.inner_box.top_left[0]
        y = self.inner_box.top_left[1]

        gaps = self.gap.column * (len(self.columns) - 1)

        y_shift = 0
        for row_index, row in enumerate(self.rows):
            x_shift = 0
            row_max_height = max(element._get_height() for element in row)
            auto = sum(element._get_width() for column, element in zip(self.columns, row) if column == 'auto')
            for column_index, (column, element) in enumerate(zip(self.columns, row)):
                if column == 'auto':
                    outer_width = element._get_width()
                else:
                    fraction = (self.inner_box.width - auto - gaps) / self.columns.sum
                    outer_width = fraction * column

                outer_height = row_max_height if element.height is MISSING else element._get_height()

                if self.align == 'start':
                    align_offset = 0
                elif self.align == 'center':
                    align_offset = (row_max_height - outer_height) / 2
                elif self.align == 'end':
                    align_offset = row_max_height - outer_height
                else:
                    align_offset = 0

                element._update(
                    x=x + x_shift + self.gap.column * column_index,
                    y=y + y_shift + self.gap.row * row_index + align_offset,
                    w=outer_width,
                    h=outer_height,
                )

                x_shift += outer_width
            y_shift += row_max_height


class Layout(Element):
    def __init__(
        self,
        *children: Element,
        width: float = MISSING,
        height: float = MISSING,
        padding: Optional[Indentation] = MISSING,
        border: Optional[Indentation] = MISSING,
        outline: Optional[int] = MISSING,
    ):
        super().__init__(*children, width=width, height=height, padding=padding, border=border, outline=outline)
        self._update(0, 0, self._get_width(), self._get_height())


def pad_bbox(bbox: tuple[float, float, float, float], padding: Indentation):
    return bbox[0] - padding.left, bbox[1] - padding.top, bbox[2] + padding.right, bbox[3] + padding.bottom


def account_draw_offset(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float, float, float]:
    return x1, y1, x2 - 1, y2 - 1


def create_panels(
    count: int,
    *,
    width: float = MISSING,
    height: float = MISSING,
    padding: Optional[Indentation] = MISSING,
    border: Optional[Indentation] = MISSING,
    outline: Optional[int] = MISSING,
) -> list[Panel]:
    return [Panel(width=width, height=height, padding=padding, border=border, outline=outline) for _ in range(count)]
