from io import BytesIO
from pathlib import Path
from typing import Protocol, Union, cast

from cairosvg import svg2png  # pyright: ignore[reportMissingTypeStubs,reportUnknownVariableType]

from ..cache import BytesCache

# fmt: off
__all__ = (
    'AssetLoader',
)
# fmt: on


class AssetLoaderP(Protocol):
    def open(self, path: Union[str, Path]) -> BytesIO: ...


class AssetLoader:
    def __init__(
        self,
        asset_paths: dict[str, Union[str, Path]],
        *,
        max_buffer_size: int = 5 * 1024 * 1024,
    ) -> None:
        """Image loader with in-memory cache for local assets.

        Parameters
        ----------
        asset_paths : dict[str, str | Path]
            Mapping of asset paths. Example: `{'': '/etc/files/{path}.webp'}`.
        max_buffer_size : int, optional
            Maximum cache buffer size in bytes. Defaults to 5MB.
        """

        self.asset_paths = {key: Path(value) for key, value in asset_paths.items()}
        self._buffer: BytesCache[str] = BytesCache(max_size=max_buffer_size)

    def _resolve_path(self, path: Path) -> Path:
        dirname = str(path.parent)
        key = max(key for key in self.asset_paths.keys() if dirname.startswith(key))

        return Path(str(self.asset_paths[key]).format(path=path))

    def _get_file(self, path: Path) -> bytes:
        resolved = self._resolve_path(path)

        str_path = str(resolved)
        if str_path in self._buffer:
            return self._buffer[str_path]

        file = resolved.read_bytes()
        if resolved.suffix == '.svg':
            file = cast(bytes, svg2png(file, scale=2))  # Have to cast here to prevent Unknown

        self._buffer[str_path] = file
        return file

    def open(self, path: Union[str, Path]) -> BytesIO:
        file = self._get_file(Path(path))
        return BytesIO(file)
