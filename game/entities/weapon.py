import math

import pygame as pg

from game.entities.player import Player


class Weapon(pg.sprite.Sprite):
    def __init__(self, image: pg.Surface, player: Player):
        super().__init__()
        self.image = image
        self.rect = image.get_rect()
        self.player = player
        self.pos = pg.Vector2((0,0))

    def update(self) -> None:
        x2 = self.player.pos.x + 25 * math.cos(self.player.angle)
        y2 = self.player.pos.y + 25 * math.sin(self.player.angle)
        self.pos = pg.Vector2((x2, y2))

        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.image = pg.transform.rotate(self.image, self.player.angle)
        print(self.pos)
    def draw(self, surface: pg.Surface) -> None:

        surface.blit(self.image, self.rect)
