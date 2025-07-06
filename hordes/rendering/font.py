from io import BytesIO
from pathlib import Path
from typing import Protocol, Union

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

__all__ = ('FontLoader',)


class FontLoaderP(Protocol):
    def get_font(self, weight: int, size: float = ...) -> FreeTypeFont: ...


class FontLoader:
    def __init__(self, font_paths: dict[int, Union[str, Path]]):
        self.font_paths = dict(sorted(((key, Path(value)) for key, value in font_paths.items()), reverse=True))

        self._cache: dict[int, FreeTypeFont] = {}
        self._variants: dict[int, dict[float, FreeTypeFont]] = {}

    def _select_weight_key(self, weight: int) -> int:
        for key in self.font_paths:
            if weight >= key:
                return key

        raise ValueError

    def _open_file(self, weight: int) -> FreeTypeFont:
        file = self.font_paths[weight].read_bytes()

        with BytesIO(file) as f:
            font = ImageFont.truetype(f)

        return font

    def _get_file(self, weight: int) -> FreeTypeFont:
        if weight in self._cache:
            return self._cache[weight]

        font = self._open_file(weight)

        self._cache[weight] = font
        return font

    def _get_variant(self, weight: int, size: float) -> FreeTypeFont:
        if weight not in self._variants:
            self._variants[weight] = {}

        if size not in self._variants[weight]:
            self._variants[weight][size] = self._get_file(weight).font_variant(size=size)

        return self._variants[weight][size]

    def get_font(self, weight: int, size: float = 16) -> FreeTypeFont:
        key = self._select_weight_key(weight)
        font = self._get_variant(key, size=size)

        return font
