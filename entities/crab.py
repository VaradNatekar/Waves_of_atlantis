
import pygame
from core.settings import *


class Crab:

    def __init__(self, x, y):

        # COLLISION
        self.rect = pygame.Rect(
            x, y, BLOCK_SIZE, BLOCK_SIZE
        )

        # HEALTH
        self.max_health = 60
        self.health = 60
        self.alive = True

        # MOVEMENT
        self.speed = 1.5
        self.direction = 1

        # COMBAT
        self.damage = 3
        self.attack_range = 35
        self.attack_cooldown = 60
        self.attack_timer = 0

        # DAMAGE EFFECT
        self.hit_timer = 0

    # ======================================
    # MOVEMENT AND AI
    # ======================================

    def update(self, player, world):

        if not self.alive:
            return

        if self.attack_timer > 0:
            self.attack_timer -= 1

        if self.hit_timer > 0:
            self.hit_timer -= 1

        distance = player.rect.centerx - self.rect.centerx
        vertical_distance = abs(
            player.rect.centery - self.rect.centery
        )

        # Follow player when nearby.
        if abs(distance) < BLOCK_SIZE * 8:

            if distance > 0:
                self.direction = 1
            elif distance < 0:
                self.direction = -1

            if abs(distance) > self.attack_range:
                self.rect.x += int(self.direction * self.speed)

        # Attack player when close.
        if (
            abs(distance) <= self.attack_range
            and vertical_distance <= BLOCK_SIZE
            and self.attack_timer <= 0
        ):

            if player.take_damage(self.damage):
                print("CRAB ATTACK! PLAYER HP:", player.health)

            self.attack_timer = self.attack_cooldown

        self.check_world_collision(world)

    # ======================================
    # WORLD COLLISION
    # ======================================

    def check_world_collision(self, world):

        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.right > GRID_WIDTH * BLOCK_SIZE:
            self.rect.right = GRID_WIDTH * BLOCK_SIZE

        left = max(0, self.rect.left // BLOCK_SIZE)
        right = min(GRID_WIDTH - 1, self.rect.right // BLOCK_SIZE)

        top = max(0, self.rect.top // BLOCK_SIZE)
        bottom = min(GRID_HEIGHT - 1, self.rect.bottom // BLOCK_SIZE)

        for y in range(top, bottom + 1):
            for x in range(left, right + 1):

                block = world[y][x]

                if block in ("air", "water"):
                    continue

                block_rect = pygame.Rect(
                    x * BLOCK_SIZE,
                    y * BLOCK_SIZE,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )

                if self.rect.colliderect(block_rect):
                    if self.direction > 0:
                        self.rect.right = block_rect.left
                    else:
                        self.rect.left = block_rect.right

    # ======================================
    # TAKE DAMAGE
    # ======================================

    def take_damage(self, amount):

        if not self.alive:
            return

        self.health = max(0, self.health - amount)
        self.hit_timer = 8

        print("CRAB HP:", self.health)

        if self.health <= 0:
            self.alive = False
            print("CRAB DEFEATED!")

    # ======================================
    # DRAW
    # ======================================

    def draw(self, screen, camera):

        if not self.alive:
            return

        screen_x, screen_y = camera.apply(
            self.rect.x,
            self.rect.y
        )

        # Crab body.
        crab_color = (
            (255, 255, 255)
            if self.hit_timer > 0
            else (190, 55, 45)
        )

        pygame.draw.ellipse(
            screen,
            crab_color,
            (
                screen_x,
                screen_y + 8,
                self.rect.width,
                self.rect.height - 8
            )
        )

        # Eyes.
        eye_y = screen_y + 10

        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (screen_x + 9, eye_y),
            3
        )

        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (screen_x + self.rect.width - 9, eye_y),
            3
        )

        # Claws.
        pygame.draw.circle(
            screen,
            (220, 75, 50),
            (screen_x - 3, screen_y + 20),
            6
        )

        pygame.draw.circle(
            screen,
            (220, 75, 50),
            (screen_x + self.rect.width + 3, screen_y + 20),
            6
        )

        # Health bar.
        bar_width = self.rect.width
        health_percent = self.health / self.max_health

        pygame.draw.rect(
            screen,
            (35, 35, 35),
            (screen_x, screen_y - 8, bar_width, 5)
        )

        pygame.draw.rect(
            screen,
            (220, 40, 40),
            (
                screen_x,
                screen_y - 8,
                int(bar_width * health_percent),
                5
            )
        )
