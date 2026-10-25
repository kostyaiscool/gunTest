import pygame as pg

from engine import ConfirmScene, Menu, MenuScene, register_scene


@register_scene("pause")
class PauseScene(MenuScene):
    title = "pause.title"
    is_overlay = True  # игра видна под затемнением и не обновляется

    def build(self, menu: Menu) -> None:
        menu.button("pause.resume", self.manager.pop)
        menu.button("pause.restart", lambda: self.manager.switch("gameplay"))
        menu.button("menu.settings", lambda: self.manager.push("settings", overlay=True))
        menu.button("pause.main_menu", self.to_main_menu)
        menu.button("menu.quit", self.app.quit)

    def handle_event(self, event: pg.event.Event) -> None:
        # Та же клавиша, что открыла паузу (Esc / P), закрывает её.
        if self.input.matches(event, "pause"):
            self.manager.pop()
        else:
            super().handle_event(event)

    def to_main_menu(self) -> None:
        self.manager.push(
            ConfirmScene,
            message="pause.main_menu_confirm",
            on_yes=lambda: self.manager.switch("main_menu"),
        )
