"""Настройки игрока, которые сохраняются между запусками в settings.json.

Чтобы добавить свою настройку — просто добавьте поле в dataclass ниже,
а в меню настроек — пункт с bind=(settings, "имя_поля").
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

log = logging.getLogger(__name__)


@dataclass
class Settings:
    fullscreen: bool = False
    show_fps: bool = False
    master_volume: float = 1.0
    music_volume: float = 0.6
    sfx_volume: float = 0.8
    language: str = ""  # пусто -> Config.default_language
    # Переназначенные игроком клавиши: действие -> список имён клавиш.
    keybinds: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> Settings:
        settings = cls()
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except FileNotFoundError:
            return settings
        except (OSError, ValueError) as exc:
            log.warning("Не удалось прочитать %s: %s. Используются настройки по умолчанию.", path, exc)
            return settings
        if not isinstance(data, dict):
            return settings

        for f in fields(cls):
            if f.name not in data:
                continue
            value, default = data[f.name], getattr(settings, f.name)
            if isinstance(default, bool):
                ok = isinstance(value, bool)
            elif isinstance(default, float):
                ok = isinstance(value, (int, float)) and not isinstance(value, bool)
                value = float(value) if ok else value
            else:
                ok = isinstance(value, type(default))
            if ok:
                setattr(settings, f.name, value)
            else:
                log.warning("Некорректное значение настройки %s=%r, пропущено", f.name, value)
        return settings

    def save(self, path: Path) -> None:
        path = Path(path)
        tmp = path.with_suffix(path.suffix + ".tmp")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(path)  # атомарная запись: файл не побьётся при падении
        except OSError as exc:
            log.warning("Не удалось сохранить настройки в %s: %s", path, exc)
