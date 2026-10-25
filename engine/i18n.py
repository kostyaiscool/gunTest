"""Простая локализация: assets/locales/<код>.json с плоскими ключами.

tr("menu.play") -> "Играть". Если ключа нет ни в текущем, ни в запасном
языке, возвращается сам ключ — поэтому в меню можно писать и обычный текст.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)


class I18n:
    def __init__(self, directory: Path, language: str, fallback: str):
        self.directory = Path(directory)
        self.fallback = fallback
        self._data: dict[str, dict[str, str]] = {}
        self.load()
        self.language = language if language in self._data else fallback

    def load(self) -> None:
        self._data.clear()
        for path in sorted(self.directory.glob("*.json")):
            try:
                self._data[path.stem] = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                log.warning("Не удалось загрузить локализацию %s: %s", path, exc)

    def set_language(self, code: str) -> None:
        if code in self._data:
            self.language = code
        else:
            log.warning("Нет локализации %r", code)

    def available(self) -> list[tuple[str, str]]:
        """[(код, название языка)] — готово для menu.choice()."""
        return [(code, data.get("_name", code)) for code, data in self._data.items()]

    def tr(self, key: str, default: str | None = None, **kwargs: object) -> str:
        text = self._data.get(self.language, {}).get(key)
        if text is None:
            text = self._data.get(self.fallback, {}).get(key)
        if text is None:
            text = key if default is None else default
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                log.warning("Ошибка форматирования строки %r", key)
        return text
