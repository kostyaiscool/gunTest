# Pygame Game Template

Шаблон для игр на pygame: сцены (меню, игра, пауза, настройки), плавные переходы,
меню, в которое пункты добавляются одной строкой, сохраняемые настройки,
переназначение клавиш, локализация и масштабирование под любой экран.

```bash
pip install -r requirements.txt
python main.py
python tests/test_smoke.py   # прогон всех сцен без окна
```

## Структура

```
main.py               точка входа
engine/               переиспользуемый «движок» — обычно не нужно трогать
  app.py              окно, главный цикл, горячие клавиши (F11, F3, F12)
  config.py           Config — параметры, которые задаёт разработчик
  settings.py         Settings — настройки игрока (settings.json)
  scene.py            Scene + @register_scene
  scene_manager.py    стек сцен: push / pop / replace / switch + затемнение
  input.py            ввод через действия ("up", "pause"...), а не клавиши
  assets.py           загрузка картинок/шрифтов/звуков с кэшем и заглушками
  audio.py            музыка и звуки с учётом громкости
  i18n.py             переводы из assets/locales/*.json
  ui/                 Menu, MenuScene, ConfirmScene, Theme
game/                 код вашей игры
  config.py           CONFIG: название, разрешение, клавиши, тема
  scenes/             main_menu, gameplay, pause, settings_menu, controls
  entities/           игровые объекты (Player, Coin)
assets/               images, sounds, music, fonts, locales
```

## Сцены и переходы

Сцена — класс с методами `handle_event`, `update(dt)`, `draw(surface)` и
хуками `on_enter / on_exit / on_pause / on_resume`. Сцены лежат в стеке:

| Вызов | Что делает | Пример |
|---|---|---|
| `self.manager.push("pause")` | открыть поверх текущей | пауза, диалог |
| `self.manager.pop()` | закрыть верхнюю | «Продолжить», «Назад» |
| `self.manager.replace("level_2")` | заменить верхнюю | следующий уровень |
| `self.manager.switch("main_menu")` | очистить стек и открыть | меню → игра |

`replace` и `switch` по умолчанию идут с затемнением (`fade=0.35`), `push` и `pop` — мгновенно.
Обновляется только верхняя сцена, поэтому игра под паузой замирает сама.
Сцена с `is_overlay = True` рисуется поверх предыдущей (игра видна под паузой).
Параметры передаются в конструктор: `self.manager.switch("gameplay", level=2)`.

### Новая сцена

```python
# game/scenes/game_over.py
from engine import MenuScene, register_scene

@register_scene("game_over")
class GameOverScene(MenuScene):
    title = "Игра окончена"

    def __init__(self, app, score=0, **kw):
        self.score = score
        super().__init__(app, **kw)

    def build(self, menu):
        menu.caption(lambda: f"Счёт: {self.score}")
        menu.button("Ещё раз", lambda: self.manager.switch("gameplay"))
        menu.button("pause.main_menu", lambda: self.manager.switch("main_menu"))
```

Затем добавьте модуль в `game/scenes/__init__.py` и вызывайте
`self.manager.switch("game_over", score=self.score)`.

## Меню: добавить пункт

Откройте `build()` нужной сцены и добавьте строку:

```python
menu.button("Сохранить", self.save_game)                         # кнопка
menu.button("Загрузить", self.load, enabled=lambda: has_save())  # может быть недоступна
menu.toggle("Сложный режим", bind=(self.app.settings, "hard"))   # вкл/выкл
menu.slider("Яркость", bind=(s, "brightness"), minimum=0, maximum=1, step=0.05)
menu.choice("Сложность", [("easy", "Легко"), ("hard", "Сложно")], bind=(s, "difficulty"))
menu.caption("Просто текст")
menu.spacer()
```

Подпись — ключ локализации (`"menu.play"`), обычный текст или функция
(`lambda: f"Монеты: {n}"`) для подписей, которые меняются. Вместо `bind=`
можно передать `getter, setter`, а `on_change=` вызывается после изменения.
Управление: стрелки/WASD, Enter/Space, Esc/Backspace — назад, мышь
(у слайдера клик по левой/правой половине уменьшает/увеличивает значение).

Диалог подтверждения:

```python
self.manager.push(ConfirmScene, message="Удалить сохранение?", on_yes=delete_save)
```

## Настройки игрока

Поля `engine/settings.py` автоматически сохраняются в `settings.json`.
Чтобы добавить свою настройку, добавьте поле (`difficulty: str = "normal"`)
и пункт в `game/scenes/settings_menu.py` с `bind=(s, "difficulty")`.

## Управление

Клавиши задаются в `game/config.py` (`keybinds`), а в коде проверяются действия:

```python
self.input.vector()           # Vector2 из up/down/left/right, нормализованный
self.input.is_down("jump")    # клавиша зажата
self.input.pressed("jump")    # нажата в этом кадре
self.input.matches(event, "pause")  # для handle_event
```

Действия из `rebindable` игрок может переназначить в «Настройки → Управление».

Глобальные клавиши: **F11** — полный экран, **F3** — FPS, **F12** — скриншот в `screenshots/`.

## Разрешение

Игра всегда рисует в логическом разрешении `Config.width × height` (1280×720).
Окно и полный экран масштабируются автоматически с сохранением пропорций,
координаты мыши пересчитываются pygame. Пересчитывать позиции через
`width_scale` больше не нужно.

## Локализация

`assets/locales/<код>.json` — плоский словарь `"ключ": "текст"`, поле `_name` —
название языка в меню. Новый язык = новый файл, он сразу появится в настройках.
В тексте можно использовать подстановки: `self.tr("hud.score", score=10)`.

## Ресурсы

`self.assets.image("player.png", (48, 48))`, `self.assets.font(28)`,
`self.audio.play_sound("coin.wav")`, `self.audio.play_music("game.ogg")`.
Если файла нет, игра не падает: вместо картинки появляется розовая заглушка,
звук просто не играет, а в лог пишется одно предупреждение.
Положите `menu.ogg` и `game.ogg` в `assets/music`, и музыка заиграет.
