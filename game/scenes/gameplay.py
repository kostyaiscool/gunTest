"""Пример игровой сцены: собирайте монетки. Замените своей игрой."""
import random

import pygame as pg

from engine import Scene, register_scene
from game.entities.coin import Coin
from game.entities.player import Player


@register_scene("gameplay")
class GameplayScene(Scene):
    BACKGROUND = (28, 32, 48)
    COINS = 5
    PAUSE_ON_FOCUS_LOST = True

    def __init__(self, app):
        super().__init__(app)
        self.bounds = app.screen_rect
        self.player = Player(self.assets.image("player.png", (48, 48)), self.bounds.center, speed=360)
        self.coins = [Coin(self.random_point()) for _ in range(self.COINS)]
        self.score = 0
        self.hud_font = self.assets.font(28)
        self.hint_font = self.assets.font(20)

    def random_point(self) -> tuple[int, int]:
        margin = 40
        return (random.randint(self.bounds.left + margin, self.bounds.right - margin),
                random.randint(self.bounds.top + margin, self.bounds.bottom - margin))

    # --- жизненный цикл ------------------------------------------------------
    def on_enter(self) -> None:
        self.audio.play_music("game.ogg")

    def on_pause(self) -> None:
        self.audio.pause_music()

    def on_resume(self) -> None:
        self.audio.resume_music()

    # --- цикл ----------------------------------------------------------------
    def handle_event(self, event: pg.event.Event) -> None:
        focus_lost = self.PAUSE_ON_FOCUS_LOST and event.type == pg.WINDOWFOCUSLOST
        if self.input.matches(event, "pause") or focus_lost:
            self.manager.push("pause")

    def update(self, dt: float) -> None:
        self.player.update(dt, self.input.vector(), self.bounds)
        for coin in self.coins:
            coin.update(dt)
            if self.player.rect.colliderect(coin.rect):
                self.score += 1
                coin.pos.update(self.random_point())
                self.audio.play_sound("coin.wav")

    def draw(self, surface: pg.Surface) -> None:
        surface.fill(self.BACKGROUND)
        for coin in self.coins:
            coin.draw(surface)
        self.player.draw(surface)
        self.draw_hud(surface)

    def draw_hud(self, surface: pg.Surface) -> None:
        score = self.hud_font.render(self.tr("hud.score", score=self.score), True, (240, 240, 250))
        surface.blit(score, score.get_rect(topright=(self.bounds.right - 20, 16)))
        hint = self.hint_font.render(self.tr("hud.hint"), True, (130, 135, 155))
        surface.blit(hint, hint.get_rect(midbottom=(self.bounds.centerx, self.bounds.bottom - 12)))
