"""Прогон сцен без окна: python -m pytest  (или python tests/test_smoke.py)."""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dataclasses  # noqa: E402

import pygame as pg  # noqa: E402

import game.scenes  # noqa: E402,F401
from engine import App, ConfirmScene  # noqa: E402
from game.config import CONFIG  # noqa: E402


def make_app(tmp_path: Path) -> App:
    config = dataclasses.replace(CONFIG, settings_file=tmp_path / "settings.json",
                                 screenshots_dir=tmp_path / "shots")
    app = App(config)
    app.scenes.switch("main_menu", fade=0)
    app.scenes.flush()
    return app


def key(app: App, name: str, frames: int = 1) -> None:
    pg.event.post(pg.event.Event(pg.KEYDOWN, key=pg.key.key_code(name), mod=0, unicode="", scancode=0))
    run(app, frames)


def run(app: App, frames: int = 1) -> None:
    for _ in range(frames):
        app.frame(1 / 60)


def stack(app: App) -> list[str]:
    return [s.scene_name for s in app.scenes.stack]


def test_scene_flow(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    try:
        assert stack(app) == ["main_menu"]

        key(app, "return", frames=40)  # «Играть» с затемнением
        assert stack(app) == ["gameplay"]

        game = app.scenes.top
        key(app, "escape")
        assert stack(app) == ["gameplay", "pause"]
        coin_phase = game.coins[0].phase
        run(app, 10)
        assert game.coins[0].phase == coin_phase, "игра должна стоять на паузе"

        key(app, "down")
        key(app, "down")  # «Настройки»
        key(app, "return")
        assert stack(app) == ["gameplay", "pause", "settings"]
        assert app.scenes.top.is_overlay

        settings_menu = app.scenes.top.menu
        settings_menu.select(2)  # общая громкость
        key(app, "left")
        assert app.settings.master_volume == 0.9

        key(app, "escape")
        assert stack(app) == ["gameplay", "pause"]
        assert (tmp_path / "settings.json").exists(), "настройки сохраняются при выходе из меню"

        key(app, "escape")
        assert stack(app) == ["gameplay"]
        run(app, 1)
        assert game.coins[0].phase != coin_phase, "после паузы игра продолжается"

        key(app, "escape")
        app.scenes.top.menu.select(3)  # «Главное меню» -> подтверждение
        key(app, "return")
        assert isinstance(app.scenes.top, ConfirmScene)
        key(app, "escape")  # «Нет»
        assert stack(app) == ["gameplay", "pause"]

        key(app, "return")
        app.scenes.top.menu.select(0)  # «Да»
        key(app, "return", frames=40)
        assert stack(app) == ["main_menu"]
    finally:
        app.scenes.clear()
        pg.quit()


def test_rebind(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    try:
        app.scenes.push("controls")
        app.scenes.flush()
        controls = app.scenes.top
        controls.start_rebind("up")
        key(app, "i")
        assert app.input.keys_for("up") == ["I"]
        assert app.settings.keybinds["up"] == ["i"]
        app.reset_keybinds()
        assert app.input.keys_for("up") == ["W", "UP"]
    finally:
        app.scenes.clear()
        pg.quit()


if __name__ == "__main__":
    import tempfile
    for test in (test_scene_flow, test_rebind):
        with tempfile.TemporaryDirectory() as d:
            test(Path(d))
            print(test.__name__, "OK")
