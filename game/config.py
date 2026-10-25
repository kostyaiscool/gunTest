"""Всё, что настраивает разработчик игры, — в одном месте."""
from pathlib import Path

from engine import Config, Theme

ROOT = Path(__file__).resolve().parent.parent

CONFIG = Config(
    title="Pygame Template",
    width=1280,
    height=720,
    fps=60,
    root=ROOT,
    default_language="ru",
    icon="player.png",
    debug=False,
    # Действие -> клавиши (имена как в pygame.key.name()).
    keybinds={
        "up": ["w", "up"],
        "down": ["s", "down"],
        "left": ["a", "left"],
        "right": ["d", "right"],
        "pause": ["escape", "p"],
    },
    # Эти действия игрок может переназначить в «Настройки -> Управление».
    rebindable=["up", "down", "left", "right"],
    theme=Theme(
        # font="my_font.ttf",  # положите шрифт в assets/fonts
        highlight_color=(55, 85, 165),
    ),
)
