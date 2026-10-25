from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pygame as pg

from engine.scene import Scene
from engine.ui.menu import Label, Menu

if TYPE_CHECKING:
    from engine.app import App


class MenuScene(Scene):
    """Сцена-меню: заголовок + список пунктов.

    Унаследуйтесь и переопределите build(), добавляя пункты одной строкой:

        class MyMenu(MenuScene):
            title = "menu.title"
            def build(self, menu):
                menu.button("Играть", lambda: self.manager.switch("gameplay"))
    """

    title: Label = ""
    title_size: int | None = None  # None -> theme.title_size

    def __init__(self, app: App, *, overlay: bool | None = None):
        super().__init__(app)
        if overlay is not None:
            self.is_overlay = overlay
        self.theme = app.config.theme
        self.title_font = self.assets.font(self.title_size or self.theme.title_size, self.theme.font)
        self.small_font = self.assets.font(self.theme.small_size, self.theme.font)
        self._dim: pg.Surface | None = None
        self.menu = Menu(app, theme=self.theme)
        self.build(self.menu)

    def build(self, menu: Menu) -> None:
        """Добавьте пункты меню здесь."""

    def rebuild(self) -> None:
        """Пересобрать пункты (например, если их набор зависит от состояния)."""
        selected = self.menu.selected
        self.menu.clear()
        self.build(self.menu)
        if self.menu.items:
            self.menu.select(max(selected, 0))

    def on_back(self) -> None:
        """Esc / Backspace. По умолчанию закрывает меню."""
        self.manager.pop()

    def handle_event(self, event: pg.event.Event) -> None:
        if self.input.matches(event, "back"):
            self.on_back()
        else:
            self.menu.handle_event(event)

    def update(self, dt: float) -> None:
        self.menu.update(dt)

    def draw(self, surface: pg.Surface) -> None:
        self.draw_background(surface)
        self.draw_title(surface)
        self.menu.draw(surface)

    def draw_background(self, surface: pg.Surface) -> None:
        if not self.is_overlay:
            surface.fill(self.theme.background)
            return
        if self._dim is None or self._dim.get_size() != surface.get_size():
            self._dim = pg.Surface(surface.get_size(), pg.SRCALPHA)
            self._dim.fill(self.theme.overlay_color)
        surface.blit(self._dim, (0, 0))

    def draw_title(self, surface: pg.Surface) -> None:
        text = self.menu.resolve(self.title)
        if text:
            y = int(self.app.config.height * self.theme.title_y)
            rendered = self.title_font.render(text, True, self.theme.title_color)
            surface.blit(rendered, rendered.get_rect(center=(self.app.config.width // 2, y)))

    def draw_hint(self, surface: pg.Surface, text: str) -> None:
        """Подсказка внизу экрана."""
        rendered = self.small_font.render(text, True, self.theme.caption_color)
        w, h = self.app.config.size
        surface.blit(rendered, rendered.get_rect(midbottom=(w // 2, h - 20)))


class ConfirmScene(MenuScene):
    """Диалог «Да / Нет» поверх текущей сцены.

        self.manager.push(ConfirmScene, message="Выйти?", on_yes=self.app.quit)
    """

    is_overlay = True
    title_size = 44

    def __init__(self, app: App, message: Label, on_yes: Callable[[], object],
                 on_no: Callable[[], object] | None = None, *,
                 yes: Label = "ui.yes", no: Label = "ui.no", default_no: bool = True):
        self.title = message
        self._on_yes, self._on_no = on_yes, on_no
        self._yes, self._no = yes, no
        super().__init__(app)
        if default_no:
            self.menu.select(1)

    def build(self, menu: Menu) -> None:
        menu.button(self._yes, self.accept)
        menu.button(self._no, self.on_back)

    def accept(self) -> None:
        self.manager.pop()
        self._on_yes()

    def on_back(self) -> None:
        self.manager.pop()
        if self._on_no:
            self._on_no()
