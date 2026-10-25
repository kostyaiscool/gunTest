from __future__ import annotations

import logging
import time

import pygame as pg

from engine.assets import Assets
from engine.audio import Audio
from engine.config import Config
from engine.i18n import I18n
from engine.input import Input
from engine.scene_manager import SceneManager, SceneRef
from engine.settings import Settings

log = logging.getLogger(__name__)


class App:
    """Окно, главный цикл и общие сервисы, доступные всем сценам."""

    def __init__(self, config: Config):
        self.config = config
        pg.init()

        self.settings = Settings.load(config.settings_file)
        if not self.settings.language:
            self.settings.language = config.default_language
        self.i18n = I18n(config.assets_dir / "locales", self.settings.language, config.default_language)

        self.assets = Assets(config.assets_dir)
        self._create_window()
        self.audio = Audio(self.assets, self.settings)
        self.input = Input({**config.all_keybinds(), **self.settings.keybinds})
        self.scenes = SceneManager(self, default_fade=config.fade_duration)

        self.clock = pg.time.Clock()
        self.time = 0.0  # секунд с запуска (без учёта ограничения dt)
        self.running = False

    # --- окно ----------------------------------------------------------------
    def _create_window(self) -> None:
        cfg = self.config
        pg.display.set_caption(cfg.title)
        if cfg.icon:
            try:
                pg.display.set_icon(pg.image.load(str(self.assets.path("images", cfg.icon))))
            except (pg.error, OSError) as exc:
                log.warning("Не удалось загрузить иконку: %s", exc)

        # SCALED: рисуем в логическом разрешении, pygame сам масштабирует
        # окно и пересчитывает координаты мыши.
        flags = pg.SCALED
        if cfg.resizable:
            flags |= pg.RESIZABLE
        if self.settings.fullscreen:
            flags |= pg.FULLSCREEN
        try:
            pg.display.set_mode(cfg.size, flags, vsync=int(cfg.vsync))
        except pg.error:
            pg.display.set_mode(cfg.size, flags)
        self._fullscreen = self.settings.fullscreen

    @property
    def screen(self) -> pg.Surface:
        return pg.display.get_surface()

    @property
    def screen_rect(self) -> pg.Rect:
        return pg.Rect((0, 0), self.config.size)

    def set_fullscreen(self, value: bool) -> None:
        value = bool(value)
        if value != self._fullscreen:
            try:
                pg.display.toggle_fullscreen()
                self._fullscreen = value
            except pg.error as exc:
                log.warning("Не удалось переключить полный экран: %s", exc)
        self.settings.fullscreen = self._fullscreen

    # --- язык, настройки, клавиши -------------------------------------------
    def tr(self, key: str, default: str | None = None, **kwargs: object) -> str:
        return self.i18n.tr(key, default, **kwargs)

    def set_language(self, code: str) -> None:
        self.i18n.set_language(code)
        self.settings.language = self.i18n.language

    def rebind(self, action: str, keys: list[str]) -> None:
        self.settings.keybinds[action] = list(keys)
        self.input.bind(action, keys)

    def reset_keybinds(self) -> None:
        self.settings.keybinds.clear()
        self.input.set_bindings(self.config.all_keybinds())

    def save_settings(self) -> None:
        self.settings.save(self.config.settings_file)

    def screenshot(self) -> None:
        folder = self.config.screenshots_dir
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / time.strftime("screenshot_%Y%m%d_%H%M%S.png")
        pg.image.save(self.screen, str(path))
        log.info("Скриншот сохранён: %s", path)

    # --- главный цикл --------------------------------------------------------
    def quit(self) -> None:
        self.running = False

    def run(self, first_scene: SceneRef, **kwargs) -> None:
        self.scenes.switch(first_scene, fade=0, **kwargs)
        self.scenes.flush()
        self.running = True
        try:
            while self.running and self.scenes:
                dt = min(self.clock.tick(self.config.fps) / 1000, self.config.max_dt)
                self.frame(dt)
        finally:
            self.scenes.clear()
            self.save_settings()
            pg.quit()

    def frame(self, dt: float) -> None:
        """Один кадр: события -> update -> draw. Удобно вызывать из тестов."""
        self.time += dt
        self.input.begin_frame()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
                break
            self.input.process(event)
            if not self._handle_global_event(event):
                self.scenes.handle_event(event)

        self.scenes.update(dt)
        surface = self.screen
        self.scenes.draw(surface)
        self._draw_debug(surface)
        pg.display.flip()

    def _handle_global_event(self, event: pg.event.Event) -> bool:
        if self.input.matches(event, "fullscreen"):
            self.set_fullscreen(not self._fullscreen)
        elif self.input.matches(event, "toggle_fps"):
            self.settings.show_fps = not self.settings.show_fps
        elif self.input.matches(event, "screenshot"):
            self.screenshot()
        else:
            return False
        return True

    def _draw_debug(self, surface: pg.Surface) -> None:
        if not (self.settings.show_fps or self.config.debug):
            return
        text = f"FPS {self.clock.get_fps():.0f}"
        if self.config.debug:
            text += "   " + " > ".join(map(repr, self.scenes.stack))
        font = self.assets.font(18)
        shadow = font.render(text, True, (0, 0, 0))
        surface.blit(shadow, (9, 9))
        surface.blit(font.render(text, True, (120, 255, 120)), (8, 8))
