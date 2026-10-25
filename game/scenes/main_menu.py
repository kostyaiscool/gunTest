from engine import ConfirmScene, Menu, MenuScene, register_scene


@register_scene("main_menu")
class MainMenuScene(MenuScene):
    title = "game.title"

    def build(self, menu: Menu) -> None:
        # Новый пункт = одна строка: подпись (ключ локализации или текст) + действие.
        menu.button("menu.play", lambda: self.manager.switch("gameplay"))
        menu.button("menu.settings", lambda: self.manager.push("settings"))
        menu.button("menu.quit", self.confirm_quit)

    def on_enter(self) -> None:
        self.audio.play_music("menu.ogg")

    def on_back(self) -> None:
        self.confirm_quit()

    def confirm_quit(self) -> None:
        self.manager.push(ConfirmScene, message="menu.quit_confirm", on_yes=self.app.quit)

    def draw(self, surface) -> None:
        super().draw(surface)
        self.draw_hint(surface, self.tr("menu.hint"))
