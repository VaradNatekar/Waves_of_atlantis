import pygame
from core.settings import *

class Slime:

    def __init__(self, x, y):

        self.rect = pygame.Rect(x, y, 40, 30)

        self.vel_x = 2

        self.health = 30

    def update(self, world):

        self.rect.x += self.vel_x

    def draw(self, screen, camera):

        screen_x, screen_y = camera.apply(
            self.rect.x,
            self.rect.y
        )

        pygame.draw.rect(
            screen,
            (0,255,100),
            (
                screen_x,
                screen_y,
                self.rect.width,
                self.rect.height
            )
        )