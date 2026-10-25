"""Базовый класс сцены (состояния игры) и реестр сцен по имени.

Регистрация по имени позволяет писать manager.switch("main_menu") из любой
сцены без циклических импортов между файлами сцен.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import pygame as pg

if TYPE_CHECKING:
    from engine.app import App
    from engine.assets import Assets
    from engine.audio import Audio
    from engine.input import Input
    from engine.scene_manager import SceneManager

SCENES: dict[str, type[Scene]] = {}

S = TypeVar("S", bound="type[Scene]")


def register_scene(name: str):
    """Декоратор: @register_scene("pause") class PauseScene(Scene): ..."""
    def decorator(cls: S) -> S:
        if name in SCENES and SCENES[name] is not cls:
            raise ValueError(f"Сцена {name!r} уже зарегистрирована: {SCENES[name].__name__}")
        SCENES[name] = cls
        cls.scene_name = name
        return cls
    return decorator


class Scene:
    # True — под сценой рисуется предыдущая (пауза, диалог поверх игры).
    is_overlay: bool = False
    scene_name: str = ""

    def __init__(self, app: App):
        self.app = app

    # --- короткие ссылки -----------------------------------------------------
    @property
    def manager(self) -> SceneManager:
        return self.app.scenes

    @property
    def input(self) -> Input:
        return self.app.input

    @property
    def assets(self) -> Assets:
        return self.app.assets

    @property
    def audio(self) -> Audio:
        return self.app.audio

    def tr(self, key: str, default: str | None = None, **kwargs: object) -> str:
        return self.app.tr(key, default, **kwargs)

    # --- жизненный цикл ------------------------------------------------------
    def on_enter(self) -> None:
        """Сцена добавлена в стек."""

    def on_exit(self) -> None:
        """Сцена удалена из стека."""

    def on_pause(self) -> None:
        """Поверх сцены открыли другую (например, паузу)."""

    def on_resume(self) -> None:
        """Сцена снова сверху."""

    # --- игровой цикл --------------------------------------------------------
    def handle_event(self, event: pg.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pg.Surface) -> None:
        pass

    def __repr__(self) -> str:
        return self.scene_name or type(self).__name__
