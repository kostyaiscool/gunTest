"""Переиспользуемая часть шаблона. Код конкретной игры живёт в пакете game/."""
from engine.app import App
from engine.config import Config
from engine.scene import Scene, register_scene
from engine.settings import Settings
from engine.ui import ConfirmScene, Menu, MenuScene, Theme

__all__ = ["App", "Config", "ConfirmScene", "Menu", "MenuScene", "Scene", "Settings", "Theme", "register_scene"]
