
import pygame
from core.settings import *


class Player:

    def __init__(self, x, y):

        # COLLISION
        self.rect = pygame.Rect(
            x, y, BLOCK_SIZE, BLOCK_SIZE * 2
        )

        # MOVEMENT
        self.vel_x = 0.0
        self.vel_y = 0.0

        self.speed = 4
        self.water_speed = 2.5
        self.jump_strength = -12
        self.gravity = 0.6
        self.on_ground = False

        # WATER PHYSICS
        self.in_water = False
        self.water_gravity = 0.18
        self.water_jump_strength = -3.5
        self.water_sink_speed = 3.0
        self.max_water_fall_speed = 4.0

        # HEALTH
        self.max_health = 100
        self.health = 100
        self.invincible_timer = 0

        # HEALING
        self.potions = 2
        self.potion_heal_amount = 30
        self.potion_cooldown = 0
        self.heal_timer = 0

        # OXYGEN
        self.max_oxygen = 100
        self.oxygen = 100

        self.oxygen_drain_rate = 0.12
        self.oxygen_recovery_rate = 0.25

        self.drowning_timer = 0
        self.drowning_interval = 60
        self.drowning_damage = 5

        # INPUT
        self.previous_h = False
        self.previous_f = False

        # COMBAT
        self.attack_damage = 25
        self.attack_range = 48
        self.attack_duration = 8
        self.attack_cooldown_max = 24

        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_hit_targets = set()

        # SPRITE
        self.image_original = pygame.image.load(
            "assets/player/knight.png"
        ).convert_alpha()

        self.image_original = pygame.transform.scale(
            self.image_original,
            (BLOCK_SIZE * 2, BLOCK_SIZE * 3)
        )

        self.image = self.image_original
        self.facing_right = True

    # ======================================
    # WATER DETECTION
    # ======================================

    def update_water_state(self, world):

        was_in_water = self.in_water
        self.in_water = False

        left = max(0, self.rect.left // BLOCK_SIZE)
        right = min(GRID_WIDTH - 1, self.rect.right // BLOCK_SIZE)

        top = max(0, self.rect.top // BLOCK_SIZE)
        bottom = min(GRID_HEIGHT - 1, self.rect.bottom // BLOCK_SIZE)

        for y in range(top, bottom + 1):
            for x in range(left, right + 1):

                if world[y][x] != "water":
                    continue

                water_rect = pygame.Rect(
                    x * BLOCK_SIZE,
                    y * BLOCK_SIZE,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )

                if self.rect.colliderect(water_rect):
                    self.in_water = True
                    break

            if self.in_water:
                break

        if self.in_water and not was_in_water:
            self.vel_y *= 0.4

    # ======================================
    # INPUT
    # ======================================

    def handle_input(self):

        keys = pygame.key.get_pressed()
        self.vel_x = 0

        movement_speed = (
            self.water_speed if self.in_water else self.speed
        )

        if keys[pygame.K_a]:
            self.vel_x = -movement_speed
            self.facing_right = False

        elif keys[pygame.K_d]:
            self.vel_x = movement_speed
            self.facing_right = True

        self.image = (
            pygame.transform.flip(
                self.image_original, True, False
            )
            if not self.facing_right
            else self.image_original
        )

        if self.in_water:

            if keys[pygame.K_SPACE]:
                self.vel_y = self.water_jump_strength

            elif keys[pygame.K_s]:
                self.vel_y = self.water_sink_speed

        else:

            if keys[pygame.K_SPACE] and self.on_ground:
                self.vel_y = self.jump_strength
                self.on_ground = False

    # ======================================
    # GRAVITY
    # ======================================

    def apply_gravity(self):

        if self.in_water:

            self.vel_y += self.water_gravity

            self.vel_y = min(
                self.vel_y,
                self.max_water_fall_speed
            )

            self.vel_x *= 0.90

        else:
            self.vel_y += self.gravity

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        if self.potion_cooldown > 0:
            self.potion_cooldown -= 1

    # ======================================
    # MOVEMENT
    # ======================================

    def move_and_collide(self, world):

        self.rect.x += int(self.vel_x)
        self.check_collision(world, horizontal=True)

        self.rect.y += int(self.vel_y)
        self.on_ground = False

        self.check_collision(world, horizontal=False)

        if self.rect.bottom > GRID_HEIGHT * BLOCK_SIZE:
            self.rect.bottom = GRID_HEIGHT * BLOCK_SIZE
            self.vel_y = 0
            self.on_ground = True

        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.right > GRID_WIDTH * BLOCK_SIZE:
            self.rect.right = GRID_WIDTH * BLOCK_SIZE

        self.update_water_state(world)

    # ======================================
    # COLLISION
    # ======================================

    def check_collision(self, world, horizontal):

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

                if not self.rect.colliderect(block_rect):
                    continue

                if horizontal:

                    if self.vel_x > 0:
                        self.rect.right = block_rect.left

                    elif self.vel_x < 0:
                        self.rect.left = block_rect.right

                else:

                    if self.vel_y > 0:
                        self.rect.bottom = block_rect.top
                        self.vel_y = 0
                        self.on_ground = True

                    elif self.vel_y < 0:
                        self.rect.top = block_rect.bottom
                        self.vel_y = 0

    # ======================================
    # OXYGEN
    # ======================================

    def update_oxygen(self):

        if self.in_water:
            self.oxygen -= self.oxygen_drain_rate
        else:
            self.oxygen += self.oxygen_recovery_rate

        self.oxygen = max(
            0,
            min(self.max_oxygen, self.oxygen)
        )

    # ======================================
    # POTION HEALING
    # ======================================

    def use_potion(self):

        if self.potions <= 0:
            return False

        if self.health >= self.max_health:
            return False

        if self.potion_cooldown > 0:
            return False

        self.health = min(
            self.max_health,
            self.health + self.potion_heal_amount
        )

        self.potions -= 1
        self.potion_cooldown = 30

        print("POTION USED! HP:", self.health)

        return True

    # ======================================
    # SURVIVAL SYSTEM
    # ======================================

    def update_survival(self, world):

        keys = pygame.key.get_pressed()

        # Potion key - press H once
        h_pressed = keys[pygame.K_h]

        if h_pressed and not self.previous_h:
            self.use_potion()

        self.previous_h = h_pressed

        # Oxygen
        self.update_oxygen()

        # Drowning damage
        if self.in_water and self.oxygen <= 0:

            self.drowning_timer += 1

            if self.drowning_timer >= self.drowning_interval:
                self.take_damage(self.drowning_damage)
                self.drowning_timer = 0

        else:
            self.drowning_timer = 0

        # Village healing
        tile_x = self.rect.centerx // BLOCK_SIZE

        in_village = (
            0 <= tile_x < BLOCKS_PER_SCREEN
        )

        if in_village and not self.in_water:

            self.heal_timer += 1

            if self.heal_timer >= 120:

                if self.health < self.max_health:
                    self.health = min(
                        self.max_health,
                        self.health + 1
                    )

                self.heal_timer = 0

        else:
            self.heal_timer = 0

    # ======================================
    # COMBAT INPUT AND ATTACK
    # ======================================

    def update_combat(self):

        keys = pygame.key.get_pressed()

        # Reduce attack timers.
        if self.attack_timer > 0:
            self.attack_timer -= 1

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Detect a fresh F key press.
        f_pressed = keys[pygame.K_f]

        if f_pressed and not self.previous_f:
            self.start_attack()

        self.previous_f = f_pressed

    def start_attack(self):

        if self.attack_cooldown > 0:
            return False

        if self.health <= 0:
            return False

        self.attack_timer = self.attack_duration
        self.attack_cooldown = self.attack_cooldown_max

        # Reset targets hit during the previous attack.
        self.attack_hit_targets.clear()

        print("PLAYER ATTACK!")

        return True

    # ======================================
    # ATTACK HITBOX
    # ======================================

    def get_attack_rect(self):

        if self.attack_timer <= 0:
            return None

        if self.facing_right:

            return pygame.Rect(
                self.rect.right,
                self.rect.centery - 20,
                self.attack_range,
                40
            )

        return pygame.Rect(
            self.rect.left - self.attack_range,
            self.rect.centery - 20,
            self.attack_range,
            40
        )

    # ======================================
    # DAMAGE ENEMIES
    # ======================================

    def attack_hits_enemy(self, enemy):

        attack_rect = self.get_attack_rect()

        if attack_rect is None:
            return False

        enemy_rect = getattr(enemy, "rect", None)

        if enemy_rect is None:
            return False

        enemy_id = id(enemy)

        # One hit per enemy per swing.
        if enemy_id in self.attack_hit_targets:
            return False

        if attack_rect.colliderect(enemy_rect):

            self.attack_hit_targets.add(enemy_id)

            if hasattr(enemy, "take_damage"):
                enemy.take_damage(self.attack_damage)

            return True

        return False

    # ======================================
    # PLAYER DAMAGE
    # ======================================

    def take_damage(self, amount):

        if self.invincible_timer > 0 or self.health <= 0:
            return False

        self.health = max(
            0,
            self.health - amount
        )

        self.invincible_timer = 30

        print("PLAYER HP:", self.health)

        if self.health <= 0:
            print("PLAYER DEAD")

        return True

    # ======================================
    # DRAW ATTACK EFFECT
    # ======================================

    def draw_attack(self, screen, camera):

        attack_rect = self.get_attack_rect()

        if attack_rect is None:
            return

        screen_rect = pygame.Rect(
            attack_rect.x - camera.camera_x,
            attack_rect.y - camera.camera_y,
            attack_rect.width,
            attack_rect.height
        )

        # Draw a visible sword slash.
        slash_surface = pygame.Surface(
            screen_rect.size,
            pygame.SRCALPHA
        )

        pygame.draw.arc(
            slash_surface,
            (220, 245, 255, 230),
            slash_surface.get_rect().inflate(-4, -4),
            0.2,
            2.9,
            4
        )

        screen.blit(slash_surface, screen_rect.topleft)

    # ======================================
    # DRAW PLAYER
    # ======================================

    def draw(self, screen, camera):

        sprite_x = (
            self.rect.centerx - self.image.get_width() // 2
        )

        sprite_y = (
            self.rect.bottom - self.image.get_height()
        )

        screen_x, screen_y = camera.apply(
            sprite_x, sprite_y
        )

        if self.invincible_timer > 0:
            if self.invincible_timer % 6 < 3:
                return

        screen.blit(
            self.image,
            (screen_x, screen_y)
        )

        self.draw_attack(screen, camera)
