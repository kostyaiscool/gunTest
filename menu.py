import pygame as pg
import config as cfg
from views import Text, Button, StateButton

test_text = Text("тест", 170, 10, 30, (255, 255, 255), "Sans Serif", 1)


def show_all_texts():
    test_text.draw(cfg.screen)

def play():
    cfg.stage = 2


def settings():
    cfg.stage = 3


def main():
    cfg.stage = 1

def lang():
    cfg.stage = 4

tutorial_button = StateButton(1, "тест", play, 1832, 1055, 175, 50, 1, (0, 0, 0), 24)
def show_all_buttons():
    tutorial_button.draw(cfg.screen)

def operate_all_buttons(event):
    tutorial_button.operate(event)