import pygame as pg

from engine import Menu, MenuScene, register_scene


@register_scene("controls")
class ControlsScene(MenuScene):
    """Переназначение клавиш: выбрать действие -> нажать новую клавишу."""

    title = "controls.title"
    title_size = 56

    def __init__(self, app, **kwargs):
        self.waiting_for: str | None = None
        super().__init__(app, **kwargs)

    def build(self, menu: Menu) -> None:
        for action in self.app.config.rebindable:
            # Подпись-функция пересчитывается каждый кадр — сразу видно новую клавишу.
            menu.button(lambda a=action: f"{self.tr('action.' + a)}:  {self.keys_text(a)}",
                        lambda a=action: self.start_rebind(a))
        menu.spacer()
        menu.button("controls.reset", self.app.reset_keybinds)
        menu.button("ui.back", self.on_back)

    def keys_text(self, action: str) -> str:
        return " / ".join(self.input.keys_for(action)) or "—"

    def start_rebind(self, action: str) -> None:
        self.waiting_for = action

    def handle_event(self, event: pg.event.Event) -> None:
        if self.waiting_for is None:
            super().handle_event(event)
            return
        if event.type == pg.KEYDOWN:
            if event.key != pg.K_ESCAPE:  # Esc — отмена
                self.app.rebind(self.waiting_for, [pg.key.name(event.key)])
            self.waiting_for = None

    def on_exit(self) -> None:
        self.app.save_settings()

    def draw(self, surface: pg.Surface) -> None:
        super().draw(surface)
        if self.waiting_for:
            action = self.tr("action." + self.waiting_for)
            self.draw_hint(surface, self.tr("controls.press_key", action=action))
