import pygame as pg


class Player(pg.sprite.Sprite):
    def __init__(self, image: pg.Surface, pos: tuple[float, float], speed: float):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(center=(round(pos[0]), round(pos[1])))
        self.pos = pg.Vector2(pos)  # точная позиция во float, rect — для отрисовки и коллизий
        self.speed = speed  # пикселей в секунду

    def update(self, dt: float, direction: pg.Vector2, bounds: pg.Rect) -> None:
        self.pos += direction * self.speed * dt
        half_w, half_h = self.rect.width / 2, self.rect.height / 2
        self.pos.x = max(bounds.left + half_w, min(bounds.right - half_w, self.pos.x))
        self.pos.y = max(bounds.top + half_h, min(bounds.bottom - half_h, self.pos.y))
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def draw(self, surface: pg.Surface) -> None:
        surface.blit(self.image, self.rect)
