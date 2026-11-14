import pygame
from core.settings import *

class Drop:
    def __init__(self, x, y, block_type):
        self.block_type = block_type

        self.rect = pygame.Rect(
            x * BLOCK_SIZE + BLOCK_SIZE // 4,
            y * BLOCK_SIZE + BLOCK_SIZE // 4,
            BLOCK_SIZE // 2,
            BLOCK_SIZE // 2
        )

        self.vel_y = 0
        self.gravity = 1.2

    def update(self, world):
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 12:
            self.vel_y = 12

        # Move vertically
        self.rect.y += self.vel_y

        # Check collision
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if world[y][x] == "air":
                    continue

                block_rect = pygame.Rect(
                    x * BLOCK_SIZE,
                    y * BLOCK_SIZE,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )

                if self.rect.colliderect(block_rect):
                    self.rect.bottom = block_rect.top
                    self.vel_y = 0
                    return

    def draw(self, screen, colors, camera):
        screen_x, screen_y = camera.apply(self.rect.x, self.rect.y)

        pygame.draw.rect(
            screen,
            colors[self.block_type],
            (screen_x, screen_y, self.rect.width, self.rect.height)
        )
