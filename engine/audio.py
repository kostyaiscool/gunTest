from __future__ import annotations

import logging

import pygame as pg

from engine.assets import Assets
from engine.settings import Settings

log = logging.getLogger(__name__)


class Audio:
    """Музыка и звуки с учётом громкости из настроек.

    Если звуковой карты нет — всё молча отключается.
    """

    def __init__(self, assets: Assets, settings: Settings):
        self.assets = assets
        self.settings = settings
        if not pg.mixer.get_init():
            try:
                pg.mixer.init()
            except pg.error as exc:
                log.warning("Звук отключён: %s", exc)
        self.enabled = bool(pg.mixer.get_init())
        self._music: str | None = None

    @property
    def sfx_volume(self) -> float:
        return self.settings.sfx_volume * self.settings.master_volume

    @property
    def music_volume(self) -> float:
        return self.settings.music_volume * self.settings.master_volume

    def play_sound(self, name: str | None, volume: float = 1.0) -> pg.mixer.Channel | None:
        if not self.enabled or not name:
            return None
        sound = self.assets.sound(name)
        if sound is None:
            return None
        channel = sound.play()
        if channel:
            channel.set_volume(volume * self.sfx_volume)
        return channel

    def play_music(self, name: str, *, loops: int = -1, fade_ms: int = 500, restart: bool = False) -> None:
        """Повторный вызов с тем же треком не перезапускает его."""
        if not self.enabled or (name == self._music and not restart):
            return
        path = self.assets.music_path(name)
        if path is None:
            self.stop_music()
            return
        try:
            pg.mixer.music.load(str(path))
            pg.mixer.music.set_volume(self.music_volume)
            pg.mixer.music.play(loops, fade_ms=fade_ms)
            self._music = name
        except pg.error as exc:
            log.warning("Не удалось включить музыку %s: %s", path, exc)

    def stop_music(self, fade_ms: int = 500) -> None:
        if self.enabled:
            if fade_ms:
                pg.mixer.music.fadeout(fade_ms)
            else:
                pg.mixer.music.stop()
        self._music = None

    def pause_music(self) -> None:
        if self.enabled:
            pg.mixer.music.pause()

    def resume_music(self) -> None:
        if self.enabled:
            pg.mixer.music.unpause()

    def update_volume(self) -> None:
        """Вызывать после изменения громкости в настройках."""
        if self.enabled:
            pg.mixer.music.set_volume(self.music_volume)
