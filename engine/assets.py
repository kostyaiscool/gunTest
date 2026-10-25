"""Загрузка ресурсов с кэшем.

Отсутствующий файл не роняет игру: картинка заменяется заглушкой,
звук просто не играет, а в лог пишется одно предупреждение.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pygame as pg

log = logging.getLogger(__name__)

# Системные шрифты с кириллицей (берётся первый найденный).
DEFAULT_SYSFONTS = "segoeui,arial,dejavusans,liberationsans,freesans"


class Assets:
    def __init__(self, root: Path):
        self.root = Path(root)
        self._images: dict[tuple, pg.Surface] = {}
        self._fonts: dict[tuple, pg.font.Font] = {}
        self._sounds: dict[str, pg.mixer.Sound | None] = {}
        self._missing: set[Path] = set()

    def path(self, *parts: str) -> Path:
        return self.root.joinpath(*parts)

    def _warn_missing(self, path: Path, reason: object = "файл не найден") -> None:
        if path not in self._missing:
            self._missing.add(path)
            log.warning("Ресурс недоступен (%s): %s", reason, path)

    # --- картинки ------------------------------------------------------------
    def image(self, name: str, size: tuple[int, int] | None = None, *, alpha: bool = True) -> pg.Surface:
        key = (name, tuple(size) if size else None, alpha)
        if key in self._images:
            return self._images[key]

        path = self.path("images", name)
        try:
            img = pg.image.load(str(path))
            img = img.convert_alpha() if alpha else img.convert()
        except (pg.error, OSError) as exc:
            self._warn_missing(path, exc)
            img = self._placeholder(size or (32, 32))
        if size and img.get_size() != tuple(size):
            img = pg.transform.smoothscale(img, size)

        self._images[key] = img
        return img

    @staticmethod
    def _placeholder(size: tuple[int, int]) -> pg.Surface:
        surf = pg.Surface(size, pg.SRCALPHA)
        surf.fill((255, 0, 255))
        cell = max(4, min(size) // 4)
        for y in range(0, size[1], cell):
            for x in range((y // cell) % 2 * cell, size[0], cell * 2):
                surf.fill((0, 0, 0), (x, y, cell, cell))
        return surf

    # --- шрифты --------------------------------------------------------------
    def font(self, size: int, name: str | None = None) -> pg.font.Font:
        """name: файл из assets/fonts (*.ttf/*.otf), имя системного шрифта или None."""
        key = (name, size)
        if key in self._fonts:
            return self._fonts[key]

        font = None
        if name and Path(name).suffix.lower() in (".ttf", ".otf"):
            path = self.path("fonts", name)
            try:
                font = pg.font.Font(str(path), size)
            except (pg.error, OSError) as exc:
                self._warn_missing(path, exc)
        if font is None:
            font = pg.font.SysFont(name if name and not Path(name).suffix else DEFAULT_SYSFONTS, size)

        self._fonts[key] = font
        return font

    # --- звук ----------------------------------------------------------------
    def sound(self, name: str) -> pg.mixer.Sound | None:
        if name in self._sounds:
            return self._sounds[name]
        sound = None
        if pg.mixer.get_init():
            path = self.path("sounds", name)
            try:
                sound = pg.mixer.Sound(str(path))
            except (pg.error, OSError) as exc:
                self._warn_missing(path, exc)
        self._sounds[name] = sound
        return sound

    def music_path(self, name: str) -> Path | None:
        path = self.path("music", name)
        if path.is_file():
            return path
        if path not in self._missing:  # музыка необязательна — не предупреждение
            self._missing.add(path)
            log.info("Музыка не найдена: %s", path)
        return None

    def clear(self) -> None:
        self._images.clear()
        self._fonts.clear()
        self._sounds.clear()
