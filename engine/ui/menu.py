"""Вертикальное меню с управлением клавиатурой и мышью.

    menu.button("menu.play", start_game)
    menu.toggle("settings.fullscreen", bind=(settings, "fullscreen"))
    menu.slider("settings.music_volume", bind=(settings, "music_volume"), on_change=...)
    menu.choice("settings.language", [("ru", "Русский"), ("en", "English")], get, set)

Подпись (label) — ключ локализации, обычный текст или функция, возвращающая
строку (для подписей, которые меняются на лету).
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, Callable, Sequence, Union

import pygame as pg

from engine.ui.theme import Theme

if TYPE_CHECKING:
    from engine.app import App

Label = Union[str, Callable[[], str]]
Getter = Callable[[], Any]
Setter = Callable[[Any], None]
Enabled = Union[bool, Callable[[], bool]]
Options = Union[Sequence[tuple[Any, Label]], Callable[[], Sequence[tuple[Any, Label]]]]


def _accessors(getter: Getter | None, setter: Setter | None,
               bind: tuple[object, str] | None, on_change: Setter | None) -> tuple[Getter, Setter]:
    if bind is not None:
        obj, attr = bind
        getter = lambda: getattr(obj, attr)  # noqa: E731
        setter = lambda value: setattr(obj, attr, value)  # noqa: E731
    if getter is None or setter is None:
        raise ValueError("Передайте getter и setter или bind=(объект, 'атрибут')")
    if on_change is None:
        return getter, setter
    base_setter = setter

    def changed(value: Any) -> None:
        base_setter(value)
        on_change(value)
    return getter, changed


# --- пункты меню -------------------------------------------------------------
class MenuItem:
    selectable = True

    def __init__(self, label: Label, *, enabled: Enabled = True):
        self.label = label
        self._enabled = enabled
        self.rect = pg.Rect(0, 0, 0, 0)

    @property
    def enabled(self) -> bool:
        return self._enabled() if callable(self._enabled) else self._enabled

    def text(self, menu: Menu) -> str:
        return menu.resolve(self.label)

    def height(self, menu: Menu) -> int:
        return menu.font.get_height() + menu.theme.padding_y * 2

    def activate(self, menu: Menu) -> None:
        """Enter / клик."""

    def adjust(self, menu: Menu, step: int) -> bool:
        """Стрелки влево/вправо. Вернуть True, если значение изменилось."""
        return False

    def click(self, menu: Menu, pos: tuple[int, int]) -> None:
        self.activate(menu)
        menu.play(menu.theme.select_sound)


class Button(MenuItem):
    def __init__(self, label: Label, action: Callable[[], Any], *, enabled: Enabled = True):
        super().__init__(label, enabled=enabled)
        self.action = action

    def activate(self, menu: Menu) -> None:
        self.action()


class Toggle(MenuItem):
    def __init__(self, label: Label, getter: Getter, setter: Setter, *, enabled: Enabled = True):
        super().__init__(label, enabled=enabled)
        self.get, self.set = getter, setter

    def text(self, menu: Menu) -> str:
        state = menu.app.tr("ui.on", "On") if self.get() else menu.app.tr("ui.off", "Off")
        return f"{menu.resolve(self.label)}: {state}"

    def activate(self, menu: Menu) -> None:
        self.set(not self.get())

    def adjust(self, menu: Menu, step: int) -> bool:
        self.activate(menu)
        return True


class _Stepper(MenuItem):
    """Пункт со значением, которое листается влево/вправо."""

    def click(self, menu: Menu, pos: tuple[int, int]) -> None:
        if self.adjust(menu, -1 if pos[0] < self.rect.centerx else 1):
            menu.play(menu.theme.move_sound)


class Slider(_Stepper):
    def __init__(self, label: Label, getter: Getter, setter: Setter, *, minimum: float = 0.0,
                 maximum: float = 1.0, step: float = 0.1, fmt: Callable[[float], str] | None = None,
                 enabled: Enabled = True):
        super().__init__(label, enabled=enabled)
        self.get, self.set = getter, setter
        self.minimum, self.maximum, self.step = minimum, maximum, step
        if fmt is None:
            fmt = (lambda v: f"{round(v * 100)}%") if (minimum, maximum) == (0, 1) else (lambda v: f"{v:g}")
        self.fmt = fmt

    def text(self, menu: Menu) -> str:
        return f"{menu.resolve(self.label)}:  <  {self.fmt(self.get())}  >"

    def adjust(self, menu: Menu, step: int) -> bool:
        old = self.get()
        steps = round((old - self.minimum) / self.step) + step
        new = round(min(self.maximum, max(self.minimum, self.minimum + steps * self.step)), 6)
        if new != old:
            self.set(new)
            return True
        return False


class Choice(_Stepper):
    def __init__(self, label: Label, options: Options, getter: Getter, setter: Setter,
                 *, wrap: bool = True, enabled: Enabled = True):
        super().__init__(label, enabled=enabled)
        self._options = options
        self.get, self.set = getter, setter
        self.wrap = wrap

    @property
    def options(self) -> Sequence[tuple[Any, Label]]:
        return self._options() if callable(self._options) else self._options

    def _index(self) -> int:
        current = self.get()
        return next((i for i, (value, _) in enumerate(self.options) if value == current), 0)

    def text(self, menu: Menu) -> str:
        options = self.options
        value_label = menu.resolve(options[self._index()][1]) if options else "-"
        return f"{menu.resolve(self.label)}:  <  {value_label}  >"

    def activate(self, menu: Menu) -> None:
        self.adjust(menu, 1)

    def adjust(self, menu: Menu, step: int) -> bool:
        options = self.options
        if not options:
            return False
        i = self._index() + step
        i = i % len(options) if self.wrap else max(0, min(len(options) - 1, i))
        if options[i][0] == self.get():
            return False
        self.set(options[i][0])
        return True


class Caption(MenuItem):
    """Невыбираемая строка текста."""
    selectable = False


class Spacer(MenuItem):
    selectable = False

    def __init__(self, size: int | None = None):
        super().__init__("")
        self.size = size

    def height(self, menu: Menu) -> int:
        return self.size if self.size is not None else menu.font.get_height() // 2


# --- само меню ---------------------------------------------------------------
class Menu:
    def __init__(self, app: App, *, theme: Theme | None = None,
                 center: tuple[int, int] | None = None, font_size: int | None = None):
        self.app = app
        self.theme = theme or app.config.theme
        w, h = app.config.size
        self.center = center or (w // 2, int(h * self.theme.menu_center_y))
        self.font = app.assets.font(font_size or self.theme.item_size, self.theme.font)
        self.items: list[MenuItem] = []
        self.selected = -1
        self._highlight: list[float] | None = None  # x, y, w, h — анимируется

    # --- построение ----------------------------------------------------------
    def add(self, item: MenuItem) -> MenuItem:
        self.items.append(item)
        if self.selected < 0 and self._can_select(item):
            self.selected = len(self.items) - 1
        return item

    def button(self, label: Label, action: Callable[[], Any], *, enabled: Enabled = True) -> Button:
        return self.add(Button(label, action, enabled=enabled))

    def toggle(self, label: Label, getter: Getter | None = None, setter: Setter | None = None, *,
               bind: tuple[object, str] | None = None, on_change: Setter | None = None,
               enabled: Enabled = True) -> Toggle:
        return self.add(Toggle(label, *_accessors(getter, setter, bind, on_change), enabled=enabled))

    def slider(self, label: Label, getter: Getter | None = None, setter: Setter | None = None, *,
               bind: tuple[object, str] | None = None, on_change: Setter | None = None,
               minimum: float = 0.0, maximum: float = 1.0, step: float = 0.1,
               fmt: Callable[[float], str] | None = None, enabled: Enabled = True) -> Slider:
        return self.add(Slider(label, *_accessors(getter, setter, bind, on_change), minimum=minimum,
                               maximum=maximum, step=step, fmt=fmt, enabled=enabled))

    def choice(self, label: Label, options: Options, getter: Getter | None = None,
               setter: Setter | None = None, *, bind: tuple[object, str] | None = None,
               on_change: Setter | None = None, wrap: bool = True, enabled: Enabled = True) -> Choice:
        return self.add(Choice(label, options, *_accessors(getter, setter, bind, on_change),
                               wrap=wrap, enabled=enabled))

    def caption(self, label: Label) -> Caption:
        return self.add(Caption(label))

    def spacer(self, size: int | None = None) -> Spacer:
        return self.add(Spacer(size))

    def clear(self) -> None:
        self.items.clear()
        self.selected = -1

    # --- выбор ---------------------------------------------------------------
    @staticmethod
    def _can_select(item: MenuItem) -> bool:
        return item.selectable and item.enabled

    @property
    def current(self) -> MenuItem | None:
        if 0 <= self.selected < len(self.items):
            return self.items[self.selected]
        return None

    def select(self, index: int) -> None:
        """Выбрать пункт по индексу (или ближайший доступный после него)."""
        n = len(self.items)
        for offset in range(n):
            i = (index + offset) % n
            if self._can_select(self.items[i]):
                self.selected = i
                return
        self.selected = -1

    def move(self, step: int) -> None:
        n = len(self.items)
        i = self.selected
        for _ in range(n):
            i = (i + step) % n
            if self._can_select(self.items[i]):
                if i != self.selected:
                    self.selected = i
                    self.play(self.theme.move_sound)
                return

    # --- ввод ----------------------------------------------------------------
    def handle_event(self, event: pg.event.Event) -> bool:
        """Вернуть True, если событие обработано меню."""
        inp = self.app.input
        item = self.current
        if item is not None and not self._can_select(item):  # пункт стал недоступен
            self.select(self.selected)
            item = self.current

        if inp.matches(event, "ui_up"):
            self.move(-1)
        elif inp.matches(event, "ui_down"):
            self.move(1)
        elif inp.matches(event, "ui_left") or inp.matches(event, "ui_right"):
            step = -1 if inp.matches(event, "ui_left") else 1
            if item and item.adjust(self, step):
                self.play(self.theme.move_sound)
        elif inp.matches(event, "confirm"):
            if item:
                self.play(self.theme.select_sound)
                item.activate(self)
        elif event.type == pg.MOUSEMOTION:
            i = self._item_at(event.pos)
            if i is not None and i != self.selected:
                self.selected = i
                self.play(self.theme.move_sound)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            i = self._item_at(event.pos)
            if i is None:
                return False
            self.selected = i
            self.items[i].click(self, event.pos)
        else:
            return False
        return True

    def _item_at(self, pos: tuple[int, int]) -> int | None:
        for i, item in enumerate(self.items):
            if self._can_select(item) and item.rect.collidepoint(pos):
                return i
        return None

    # --- отрисовка -----------------------------------------------------------
    def resolve(self, label: Label) -> str:
        return label() if callable(label) else self.app.tr(label)

    def play(self, sound: str | None) -> None:
        self.app.audio.play_sound(sound)

    def layout(self) -> None:
        heights = [item.height(self) for item in self.items]
        total = sum(heights) + self.theme.item_spacing * max(0, len(heights) - 1)
        cx, y = self.center[0], self.center[1] - total // 2
        for item, h in zip(self.items, heights):
            w = self.font.size(item.text(self))[0] + self.theme.padding_x * 2 if item.label else 0
            item.rect = pg.Rect(0, 0, w, h)
            item.rect.midtop = (cx, y)
            y += h + self.theme.item_spacing

    def update(self, dt: float) -> None:
        self.layout()
        item = self.current
        if item is None:
            self._highlight = None
            return
        target = [*item.rect]
        if self._highlight is None:
            self._highlight = [float(v) for v in target]
        else:
            k = 1 - math.exp(-self.theme.highlight_speed * dt)
            self._highlight = [a + (b - a) * k for a, b in zip(self._highlight, target)]

    def draw(self, surface: pg.Surface) -> None:
        self.layout()
        theme = self.theme
        if self._highlight is not None and self.current is not None:
            rect = pg.Rect(*(round(v) for v in self._highlight))
            pg.draw.rect(surface, theme.highlight_color, rect, border_radius=theme.border_radius)

        for i, item in enumerate(self.items):
            if not item.label:
                continue
            if not item.selectable:
                color = theme.caption_color
            elif not item.enabled:
                color = theme.disabled_color
            elif i == self.selected:
                color = theme.selected_color
            else:
                color = theme.text_color
            text = self.font.render(item.text(self), True, color)
            surface.blit(text, text.get_rect(center=item.rect.center))
