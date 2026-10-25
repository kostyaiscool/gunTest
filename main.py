import logging

import game.scenes  # noqa: F401  — регистрирует сцены
from engine import App
from game.config import CONFIG


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    App(CONFIG).run("main_menu")


if __name__ == "__main__":
    main()
