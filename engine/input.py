"""Ввод через «действия» вместо конкретных клавиш.

Код игры спрашивает input.is_down("left"), а не keys[pg.K_a] — поэтому
клавиши можно менять в конфиге или в меню, не трогая логику.
"""
from __future__ import annotations

import logging

import pygame as pg

log = logging.getLogger(__name__)


def key_code(name: str) -> int | None:
    try:
        return pg.key.key_code(name)
    except ValueError:
        log.warning("Неизвестная клавиша: %r", name)
        return None


def key_label(code: int) -> str:
    return pg.key.name(code).upper() or f"#{code}"


class Input:
    def __init__(self, bindings: dict[str, list[str]]):
        self._bindings: dict[str, list[int]] = {}
        self._pressed: set[str] = set()
        self._released: set[str] = set()
        self.set_bindings(bindings)

    # --- привязки -----------------------------------------------------------
    def set_bindings(self, bindings: dict[str, list[str]]) -> None:
        self._bindings.clear()
        for action, names in bindings.items():
            self.bind(action, names)

    def bind(self, action: str, names: list[str]) -> None:
        codes = [code for code in map(key_code, names) if code is not None]
        self._bindings[action] = codes

    def keys_for(self, action: str) -> list[str]:
        """Названия клавиш действия для показа игроку."""
        return [key_label(code) for code in self._bindings.get(action, [])]

    # --- обработка событий ---------------------------------------------------
    def begin_frame(self) -> None:
        self._pressed.clear()
        self._released.clear()

    def process(self, event: pg.event.Event) -> None:
        if event.type not in (pg.KEYDOWN, pg.KEYUP):
            return
        target = self._pressed if event.type == pg.KEYDOWN else self._released
        for action, codes in self._bindings.items():
            if event.key in codes:
                target.add(action)

    def matches(self, event: pg.event.Event, action: str) -> bool:
        """Событие — нажатие клавиши, привязанной к действию."""
        return event.type == pg.KEYDOWN and event.key in self._bindings.get(action, ())

    # --- опрос состояния -----------------------------------------------------
    def is_down(self, action: str) -> bool:
        keys = pg.key.get_pressed()
        return any(keys[code] for code in self._bindings.get(action, ()))

    def pressed(self, action: str) -> bool:
        """Клавиша действия нажата именно в этом кадре."""
        return action in self._pressed

    def released(self, action: str) -> bool:
        return action in self._released

    def axis(self, negative: str, positive: str) -> float:
        return float(self.is_down(positive)) - float(self.is_down(negative))

    def vector(self, left: str = "left", right: str = "right",
               up: str = "up", down: str = "down") -> pg.Vector2:
        """Нормализованное направление (диагональ не быстрее прямой)."""
        v = pg.Vector2(self.axis(left, right), self.axis(up, down))
        if v.length_squared() > 0:
            v.normalize_ip()
        return v
