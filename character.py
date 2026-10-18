from config import width_scale, height, height_scale, width
import pygame as pg

class Character:
    def __init__(self, image, x, y, speed, max_hp):
        self.formula = int(30 * width_scale)
        self.skin = pg.image.load(image)
        self.skin = pg.transform.scale(self.skin, (self.formula, self.formula))
        self.rect = self.skin.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.speed = speed * width_scale
        self.hp = max_hp
        self.max_hp = max_hp

    def show_char(self, screen):
        screen.blit(self.skin, (self.rect.x, self.rect.y))

    def move(self, dir):
        if dir == 'up' and self.rect.y > 0:
            self.rect.y -= self.speed
        elif dir == 'down' and self.rect.y < height - 30 * height_scale:
            self.rect.y += self.speed
        if dir == 'left' and self.rect.x > 0:
            self.rect.x -= self.speed
        elif dir == 'right' and self.rect.x < width - 30 * width_scale:
            self.rect.x += self.speed