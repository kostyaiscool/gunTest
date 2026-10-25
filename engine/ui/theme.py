from __future__ import annotations

from dataclasses import dataclass

Color = tuple[int, int, int]


@dataclass
class Theme:
    """Внешний вид меню. Создайте свою Theme(...) в game/config.py."""

    font: str | None = None  # файл из assets/fonts, имя системного шрифта или None
    title_size: int = 72
    item_size: int = 36
    small_size: int = 22

    background: Color = (18, 20, 32)
    title_color: Color = (240, 240, 250)
    text_color: Color = (175, 180, 200)
    selected_color: Color = (255, 255, 255)
    disabled_color: Color = (85, 90, 105)
    caption_color: Color = (140, 145, 165)
    highlight_color: Color = (55, 85, 165)
    overlay_color: tuple[int, int, int, int] = (0, 0, 0, 170)  # затемнение под паузой

    item_spacing: int = 10
    padding_x: int = 28
    padding_y: int = 4
    border_radius: int = 10
    highlight_speed: float = 18.0  # скорость «переезда» подсветки

    # Положение по вертикали в долях высоты экрана.
    title_y: float = 0.2
    menu_center_y: float = 0.58

    # Звуки из assets/sounds; если файла нет — просто тишина.
    move_sound: str | None = "ui_move.wav"
    select_sound: str | None = "ui_select.wav"
