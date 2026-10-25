from engine import Menu, MenuScene, register_scene


@register_scene("settings")
class SettingsScene(MenuScene):
    """Открывается и из главного меню, и из паузы (overlay=True)."""

    title = "settings.title"

    def build(self, menu: Menu) -> None:
        app, s = self.app, self.app.settings
        volume_changed = lambda _: self.audio.update_volume()  # noqa: E731

        menu.toggle("settings.fullscreen", lambda: s.fullscreen, app.set_fullscreen)
        menu.toggle("settings.show_fps", bind=(s, "show_fps"))
        menu.slider("settings.master_volume", bind=(s, "master_volume"), on_change=volume_changed)
        menu.slider("settings.music_volume", bind=(s, "music_volume"), on_change=volume_changed)
        menu.slider("settings.sfx_volume", bind=(s, "sfx_volume"), on_change=volume_changed)
        menu.choice("settings.language", app.i18n.available(), lambda: s.language, app.set_language)
        menu.button("settings.controls", lambda: self.manager.push("controls", overlay=self.is_overlay))
        menu.spacer()
        menu.button("ui.back", self.on_back)

    def on_exit(self) -> None:
        self.app.save_settings()
