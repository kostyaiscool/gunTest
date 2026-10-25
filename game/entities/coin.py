import math
import random

import pygame as pg


class Coin:
    RADIUS = 12

    def __init__(self, pos: tuple[float, float]):
        self.pos = pg.Vector2(pos)
        self.phase = random.uniform(0, math.tau)

    @property
    def rect(self) -> pg.Rect:
        r = self.RADIUS
        return pg.Rect(self.pos.x - r, self.pos.y - r, r * 2, r * 2)

    def update(self, dt: float) -> None:
        self.phase += dt * 4

    def draw(self, surface: pg.Surface) -> None:
        r = self.RADIUS + math.sin(self.phase) * 2
        pg.draw.circle(surface, (250, 200, 60), self.pos, r)
        pg.draw.circle(surface, (255, 235, 140), self.pos, r * 0.5)
