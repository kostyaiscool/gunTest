"""Стек сцен с отложенными переходами и затемнением.

* push    — открыть сцену поверх текущей (пауза, настройки, диалог);
* pop     — закрыть верхнюю и вернуться к предыдущей;
* replace — заменить верхнюю сцену;
* switch  — очистить весь стек и открыть новую (меню -> игра, игра -> меню).

Обновляется только верхняя сцена, поэтому всё, что под паузой, замирает
автоматически. Изменения стека применяются после update(), а не посреди
обработки событий — это защищает от двойных нажатий и порчи стека.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Union

import pygame as pg

from engine.scene import SCENES, Scene

if TYPE_CHECKING:
    from engine.app import App

log = logging.getLogger(__name__)

SceneRef = Union[Scene, str, type[Scene]]


class Fade:
    """Затемнение: экран темнеет, в середине меняется сцена, затем светлеет."""

    def __init__(self, duration: float, on_middle: Callable[[], None], color=(0, 0, 0)):
        self.half = max(duration / 2, 1e-3)
        self.on_middle = on_middle
        self.time = 0.0
        self.switched = False
        self._overlay = pg.Surface((1, 1))
        self._overlay.fill(color)

    @property
    def done(self) -> bool:
        return self.time >= self.half * 2

    def update(self, dt: float) -> None:
        self.time += dt
        if not self.switched and self.time >= self.half:
            self.switched = True
            self.on_middle()

    def draw(self, surface: pg.Surface) -> None:
        progress = self.time / self.half
        alpha = progress if progress < 1 else 2 - progress
        if self._overlay.get_size() != surface.get_size():
            color = self._overlay.get_at((0, 0))
            self._overlay = pg.Surface(surface.get_size())
            self._overlay.fill(color)
        self._overlay.set_alpha(int(255 * max(0.0, min(1.0, alpha))))
        surface.blit(self._overlay, (0, 0))


class SceneManager:
    def __init__(self, app: App, default_fade: float = 0.35):
        self.app = app
        self.default_fade = default_fade
        self.stack: list[Scene] = []
        self._queue: list[tuple[Callable[[], None], float]] = []
        self._transition: Fade | None = None

    # --- состояние -----------------------------------------------------------
    @property
    def top(self) -> Scene | None:
        return self.stack[-1] if self.stack else None

    @property
    def busy(self) -> bool:
        """Идёт переход или есть запрошенные, но ещё не применённые изменения."""
        return bool(self._queue) or self._transition is not None

    def __bool__(self) -> bool:
        return bool(self.stack) or bool(self._queue)

    def __contains__(self, name_or_cls: str | type[Scene]) -> bool:
        return any(self._is(s, name_or_cls) for s in self.stack)

    @staticmethod
    def _is(scene: Scene, ref: str | type[Scene]) -> bool:
        return scene.scene_name == ref if isinstance(ref, str) else isinstance(scene, ref)

    # --- публичный API -------------------------------------------------------
    def push(self, ref: SceneRef, *, fade: float = 0.0, **kwargs) -> None:
        def op() -> None:
            if self.top:
                self.top.on_pause()
            self._enter(ref, kwargs)
        self._schedule(op, fade)

    def pop(self, *, fade: float = 0.0) -> None:
        def op() -> None:
            if self.stack:
                self.stack.pop().on_exit()
                if self.top:
                    self.top.on_resume()
        self._schedule(op, fade)

    def replace(self, ref: SceneRef, *, fade: float | None = None, **kwargs) -> None:
        def op() -> None:
            if self.stack:
                self.stack.pop().on_exit()
            self._enter(ref, kwargs)
        self._schedule(op, self.default_fade if fade is None else fade)

    def switch(self, ref: SceneRef, *, fade: float | None = None, **kwargs) -> None:
        def op() -> None:
            self._exit_all()
            self._enter(ref, kwargs)
        self._schedule(op, self.default_fade if fade is None else fade)

    def pop_to(self, ref: str | type[Scene], *, fade: float = 0.0) -> None:
        """Закрыть сцены, пока сверху не окажется указанная."""
        def op() -> None:
            if ref not in self:
                log.warning("pop_to: сцены %r нет в стеке", ref)
                return
            while not self._is(self.stack[-1], ref):
                self.stack.pop().on_exit()
            self.stack[-1].on_resume()
        self._schedule(op, fade)

    def flush(self) -> None:
        """Немедленно применить все запрошенные изменения (без затемнения)."""
        while self._queue:
            op, _ = self._queue.pop(0)
            op()

    def clear(self) -> None:
        self._queue.clear()
        self._transition = None
        self._exit_all()

    # --- игровой цикл --------------------------------------------------------
    def handle_event(self, event: pg.event.Event) -> None:
        # Сцена уже попросила переход — оставшиеся события кадра ей не нужны.
        if self.busy or not self.top:
            return
        self.top.handle_event(event)

    def update(self, dt: float) -> None:
        if self.top:
            self.top.update(dt)

        if self._transition:
            self._transition.update(dt)
            if self._transition.done:
                self._transition = None
        while self._queue and self._transition is None:
            op, fade = self._queue.pop(0)
            if fade > 0:
                self._transition = Fade(fade, op)
            else:
                op()

    def draw(self, surface: pg.Surface) -> None:
        if self.stack:
            # Рисуем ближайшую непрозрачную сцену и верхний оверлей над ней.
            # Промежуточные оверлеи (пауза под диалогом) не рисуются.
            base = len(self.stack) - 1
            while base > 0 and self.stack[base].is_overlay:
                base -= 1
            if self.stack[base].is_overlay:
                surface.fill((0, 0, 0))
            self.stack[base].draw(surface)
            if base != len(self.stack) - 1:
                self.stack[-1].draw(surface)
        if self._transition:
            self._transition.draw(surface)

    # --- внутреннее ----------------------------------------------------------
    def _schedule(self, op: Callable[[], None], fade: float) -> None:
        self._queue.append((op, fade))

    def _enter(self, ref: SceneRef, kwargs: dict) -> None:
        scene = self._create(ref, kwargs)
        self.stack.append(scene)
        scene.on_enter()

    def _exit_all(self) -> None:
        while self.stack:
            self.stack.pop().on_exit()

    def _create(self, ref: SceneRef, kwargs: dict) -> Scene:
        if isinstance(ref, Scene):
            if kwargs:
                raise TypeError("Аргументы передаются только при создании сцены по имени или классу")
            return ref
        if isinstance(ref, str):
            try:
                ref = SCENES[ref]
            except KeyError:
                raise KeyError(f"Сцена {ref!r} не зарегистрирована. Есть: {', '.join(SCENES)}") from None
        return ref(self.app, **kwargs)
