import pygame as pg
import config as cfg

pg.init()


class Text:
    def __init__(self, text, x, y, size, color, font_name, stage):
        self.text = text
        self.x = int(x * cfg.width_scale)
        self.y = int(y * cfg.height_scale)
        self.size = int(size * cfg.width_scale)
        self.color = color
        self.font_name = font_name
        self.font = pg.font.SysFont(self.font_name, self.size)
        self.rendered = self.font.render(self.text, True, self.color)
        self.rect = self.rendered.get_rect(center=(self.x, self.y))
        self.stage = stage

    def update_text(self, new_text):
        self.text = new_text
        self.rendered = self.font.render(self.text, True, self.color)
        self.rect = self.rendered.get_rect(center=(self.x, self.y))

    def draw(self, surface):
        if self.stage == cfg.stage or self.stage == "DEMO":
            surface.blit(self.rendered, self.rect)

class Button:
    def __init__(self, text, method, x, y, sx, sy, color, text_size):
        self.text = text
        self.method = method
        self.x = int(x * cfg.width_scale)
        self.y = int(y * cfg.height_scale)
        self.skin = pg.Surface((sx, sy))
        self.skin.fill(color)
        self.rect = self.skin.get_rect(center=(self.x, self.y))
        self.sx = sx
        self.sy = sy
        self.text_size = text_size
        self.text = Text(self.text, self.rect.centerx / cfg.width_scale, self.rect.centery / cfg.height_scale, self.text_size, (255, 255, 255), "Comic Sans MS",
                        self.menu_stage)

    def draw(self, surface):
        surface.blit(self.skin, self.rect)
        pg.draw.rect(surface, (255, 255, 255), self.rect, int(3 * cfg.width_scale))
        self.text.draw(surface)

    def operate(self, events):
        if events.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                self.method()

class StateButton(Button):
    def __init__(self, state, text, method, x, y, sx, sy, menu_stage, color, text_size):
        super().__init__(text, method, x, y, sx, sy, menu_stage, color, text_size)
        self.state = state

    def state_to(self, state_to):
        self.state = state_to
        cfg.stage = state_to