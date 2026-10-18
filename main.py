import pygame as pg

from character import Character
from config import width, height, screen
from menu import operate_all_buttons, show_all_texts, show_all_buttons
from utils import menu_falser


def run():
    clock = pg.time.Clock()
    game = True
    color = (0, 0, 0)
    mainchar = Character("Sources/squar.png", width / 2, height / 2, 3, 30)
    while game:
        screen.fill(color)
        menu = menu_falser()
        keys = pg.key.get_pressed()
        if not menu:
            mainchar.show_char(screen)
            if keys[pg.K_UP] or keys[pg.K_w]:
                mainchar.move('up')
            elif keys[pg.K_DOWN] or keys[pg.K_s]:
                mainchar.move('down')
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                mainchar.move('left')
            elif keys[pg.K_RIGHT] or keys[pg.K_d]:
                mainchar.move('right')
        show_all_texts()
        show_all_buttons()
        pg.display.flip()
        clock.tick(60)
        events = pg.event.get()
        for e in events:
            operate_all_buttons(e)
            if e.type == pg.QUIT:
                game = False
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    game = False


run()