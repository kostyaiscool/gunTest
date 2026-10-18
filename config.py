import pygame as pg

pg.init()
info = pg.display.Info()
width = info.current_w
height = info.current_h
screen = pg.display.set_mode((width, height))

width_scale = width / 1920
height_scale = height / 1080

stage = 1
'''
1 - меню
2 - бой
'''