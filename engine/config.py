"""Конфигурация игры, которую задаёт разработчик (не игрок).

Пользовательские настройки (громкость, полный экран, язык...) лежат в
engine/settings.py и сохраняются в settings.json.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from engine.ui.theme import Theme

# Клавиши, которые нужны самому движку. Игра может переопределить любые из них
# через Config.keybinds. Имена клавиш — как в pygame.key.name(): "w", "up", "f11"...
ENGINE_KEYBINDS: dict[str, list[str]] = {
    # навигация по меню
    "ui_up": ["up", "w"],
    "ui_down": ["down", "s"],
    "ui_left": ["left", "a"],
    "ui_right": ["right", "d"],
    "confirm": ["return", "enter", "space"],
    "back": ["escape", "backspace"],
    # глобальные горячие клавиши
    "fullscreen": ["f11"],
    "toggle_fps": ["f3"],
    "screenshot": ["f12"],
}


@dataclass
class Config:
    title: str = "Pygame Game"
    # Логическое разрешение. Игра всегда рисует в этом размере, а окно/полный
    # экран масштабируется автоматически (pygame.SCALED) с сохранением пропорций.
    width: int = 1280
    height: int = 720
    fps: int = 60
    vsync: bool = True
    resizable: bool = True
    # Ограничение dt, чтобы после подвисания объекты не «телепортировались».
    max_dt: float = 0.1
    # Длительность затемнения при смене сцен по умолчанию (секунды).
    fade_duration: float = 0.35

    root: Path = field(default_factory=Path.cwd)
    assets_dir: Path | None = None  # по умолчанию root/assets
    settings_file: Path | None = None  # по умолчанию root/settings.json
    screenshots_dir: Path | None = None  # по умолчанию root/screenshots

    default_language: str = "ru"
    icon: str | None = None  # имя файла в assets/images

    # Действие -> список клавиш. Объединяется с ENGINE_KEYBINDS.
    keybinds: dict[str, list[str]] = field(default_factory=dict)
    # Действия, которые игрок может переназначить в меню «Управление».
    rebindable: list[str] = field(default_factory=list)

    theme: Theme = field(default_factory=Theme)
    debug: bool = False  # показывать стек сцен вместе с FPS

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self.assets_dir = Path(self.assets_dir or self.root / "assets")
        self.settings_file = Path(self.settings_file or self.root / "settings.json")
        self.screenshots_dir = Path(self.screenshots_dir or self.root / "screenshots")

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def all_keybinds(self) -> dict[str, list[str]]:
        return {**ENGINE_KEYBINDS, **self.keybinds}
