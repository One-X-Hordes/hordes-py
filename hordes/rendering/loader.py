from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Dict, Union, cast

import aiofiles
import aiofiles.os
from aiohttp import ClientSession
from cairosvg import svg2png  # pyright: ignore[reportMissingTypeStubs,reportUnknownVariableType]
from PIL import Image
from yarl import URL

from ..cache import BytesCache

__all__ = ('ImageLoader',)


class ImageLoader:
    def __init__(
        self,
        *,
        session: ClientSession,
        assets_url: Dict[str, Union[str, URL]],
        save_path: Union[str, Path],
        max_buffer_size=250,
    ) -> None:
        """Async image asset loader for web and local assets

        :param session: Web session to use in asset requests
        :type session: aiohttp.ClientSession
        :param assets_url: Mapping of asset paths, example: `{'/': 'https://example.com'}`
        :type assets_url: Dict[str, str | URL]
        :param save_path: Path to save assets at, defaults to {library path}/data
        :type save_path: str | Path
        """
        self.session = session
        self.assets_url = {key: URL(value) for key, value in assets_url.items()}
        self.save_path = Path(save_path).resolve()

        self._buffer: BytesCache[str] = BytesCache(max_size=max_buffer_size)

    def get_url(self, path: Path) -> URL:
        dirname = str(path.parent)
        key = max([key for key in self.assets_url.keys() if dirname.startswith(key)])

        return self.assets_url[key] / str(path)[1:]

    async def read_file(self, path: Path) -> bytes:
        async with aiofiles.open(path, mode='rb') as f:
            file = await f.read()
        return file

    async def fetch_file(self, path: Path) -> bytes:
        url = self.get_url(path)
        async with self.session.get(url) as resp:
            response = await resp.content.read()
        return response

    async def save_file(self, path: Path, file: bytes) -> None:
        exists = await aiofiles.os.path.isdir(path.parent)
        if not exists:
            await aiofiles.os.makedirs(path.parent)

        async with aiofiles.open(path, mode='wb') as f:
            await f.write(file)

    async def get_file(self, path: Path) -> bytes:
        save_path = self.save_path / str(path)[1:]
        str_save_path = str(save_path)

        if str_save_path in self._buffer:
            return self._buffer[str_save_path]

        exists = await aiofiles.os.path.exists(save_path)

        if exists:
            file = await self.read_file(save_path)
        else:
            file = await self.fetch_file(path)
            await self.save_file(save_path, file)

        if path.suffix == '.svg':
            file = cast(bytes, svg2png(file, scale=2))  # Have to cast here to prevent Unknown

        self._buffer[str_save_path] = file
        return file

    @asynccontextmanager
    async def open(self, path: Union[str, Path]) -> AsyncGenerator[Image.Image, None]:
        file = await self.get_file(Path(path))

        with Image.open(file) as img:
            yield img
