
import pygame

# Initialize Pygame BEFORE importing UI.
pygame.init()
from entities.crab import Crab
from core.settings import *
from core.world import generate_world, get_depth_level
from entities.player import Player
from entities.drop import Drop
from core.ui import (
    draw_status,
    draw_inventory,
    draw_oxygen,
    draw_health,
    draw_minimap,
)
from core.camera import Camera


# Continue with the rest of your existing main.py
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Waves of Atlantis")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 20, bold=True)


# ==================================================
# LOAD TILES
# ==================================================

TILES = {
    "grass": pygame.image.load("assets/tiles/grass.png").convert_alpha(),
    "soil": pygame.image.load("assets/tiles/soil.png").convert_alpha(),
    "stone": pygame.image.load("assets/tiles/stone.png").convert_alpha(),
    "sand": pygame.image.load("assets/tiles/sand.png").convert_alpha(),
    "wet_sand": pygame.image.load("assets/tiles/wet_sand.png").convert_alpha(),
    "water": pygame.image.load("assets/tiles/water.png").convert_alpha(),
    "path": pygame.image.load("assets/tiles/path.png").convert_alpha(),
    "wood": pygame.image.load("assets/tiles/woods.png").convert_alpha(),
    "planks": pygame.image.load("assets/tiles/planks.png").convert_alpha(),
    "leaves": pygame.image.load("assets/tiles/leaves.png").convert_alpha(),
    "roof": pygame.image.load("assets/tiles/roof.png").convert_alpha(),
    "brick": pygame.image.load("assets/tiles/brick.png").convert_alpha(),
    "window": pygame.image.load("assets/tiles/window.png").convert_alpha(),
    "door": pygame.image.load("assets/tiles/door.png").convert_alpha(),
}

for key in TILES:
    TILES[key] = pygame.transform.scale(
        TILES[key],
        (BLOCK_SIZE, BLOCK_SIZE)
    )


# ==================================================
# LOAD BACKGROUNDS
# ==================================================

mountains_bg = pygame.image.load(
    "assets/backgrounds/mountains.png"
).convert()

mountains_bg = pygame.transform.scale(
    mountains_bg,
    (1920, 600)
)

cloud_small = pygame.image.load(
    "assets/backgrounds/cloud_small.png"
).convert_alpha()

cloud_medium = pygame.image.load(
    "assets/backgrounds/cloud_medium.png"
).convert_alpha()

cloud_big = pygame.image.load(
    "assets/backgrounds/cloud_big.png"
).convert_alpha()


# ==================================================
# BACKGROUND
# ==================================================

def draw_village_background(screen, camera):
    for y in range(HEIGHT):
        ratio = y / HEIGHT

        r = int(135 - 40 * ratio)
        g = int(206 - 60 * ratio)
        b = int(235 - 80 * ratio)

        pygame.draw.line(
            screen,
            (r, g, b),
            (0, y),
            (WIDTH, y)
        )


# ==================================================
# UNDERWATER VISUAL EFFECT
# ==================================================

def draw_underwater_overlay(screen, player, camera, world):
    overlay = pygame.Surface(
        (BLOCK_SIZE, BLOCK_SIZE),
        pygame.SRCALPHA
    )

    overlay.fill((10, 100, 200, 75))

    left = max(0, player.rect.left // BLOCK_SIZE)
    right = min(GRID_WIDTH - 1, player.rect.right // BLOCK_SIZE)

    top = max(0, player.rect.top // BLOCK_SIZE)
    bottom = min(GRID_HEIGHT - 1, player.rect.bottom // BLOCK_SIZE)

    for y in range(top, bottom + 1):
        for x in range(left, right + 1):

            if world[y][x] == "water":
                screen_x, screen_y = camera.apply(
                    x * BLOCK_SIZE,
                    y * BLOCK_SIZE
                )

                screen.blit(
                    overlay,
                    (screen_x, screen_y)
                )


# ==================================================
# WORLD
# ==================================================

world = generate_world()


# ==================================================
# BLOCK COLORS
# ==================================================

COLORS = {
    "air": (135, 206, 235),
    "grass": (50, 180, 50),
    "soil": (140, 90, 40),
    "stone": (120, 120, 120),
    "brick": (150, 80, 60),
    "abyss_stone": (30, 30, 60),
    "sand": (194, 178, 128),
    "wet_sand": (160, 140, 100),
    "ruin_brick": (100, 120, 130),
    "coral": (255, 100, 100),
    "deep_stone": (40, 40, 70),
    "path": (170, 140, 90),
    "wood": (120, 70, 30),
    "planks": (160, 110, 60),
    "leaves": (40, 160, 40),
    "roof": (110, 50, 40),
    "window": (120, 180, 255),
    "door": (90, 60, 30),
    "water": (20, 100, 220),
}


# ==================================================
# PLAYER AND CAMERA
# ==================================================

player = Player(200, 100)
camera = Camera()


# ==================================================
# INVENTORY
# ==================================================

drops = []
inventory = {}
selected_item = None

# ==================================================
# SHORE GUARDIAN ENCOUNTER
# ==================================================

TOTAL_CRABS = 5
crabs = []
crabs_defeated = 0
current_crab_number = 0
sea_unlocked = False
victory_message_timer = 0

wave_font = pygame.font.SysFont("Arial", 24, bold=True)
victory_font = pygame.font.SysFont("Arial", 42, bold=True)
subtitle_font = pygame.font.SysFont("Arial", 22, bold=True)


def find_shore_spawn(world):
    for y in range(1, GRID_HEIGHT - 1):
        for x in range(1, GRID_WIDTH - 1):

            block = world[y][x]

            if block not in ("sand", "wet_sand"):
                continue

            # Crab stands on top of solid ground.
            if world[y - 1][x] != "air":
                continue

            # Look for nearby water.
            near_water = any(
                world[ny][nx] == "water"
                for ny in range(max(0, y - 2), min(GRID_HEIGHT, y + 3))
                for nx in range(max(0, x - 3), min(GRID_WIDTH, x + 4))
            )

            if near_water:
                return x * BLOCK_SIZE, y * BLOCK_SIZE - BLOCK_SIZE

    return None


shore_spawn = find_shore_spawn(world)


def spawn_next_crab():
    global current_crab_number

    if shore_spawn is None or crabs_defeated >= TOTAL_CRABS:
        return

    current_crab_number = crabs_defeated + 1
    crabs.append(Crab(*shore_spawn))
    print(f"SHORE GUARDIAN {current_crab_number}/{TOTAL_CRABS} SPAWNED")


if shore_spawn:
    spawn_next_crab()
else:
    print("WARNING: No suitable shore location found. Crab encounter not started.")

# ==================================================
# GAME LOOP
# ==================================================

running = True

while running:

    clock.tick(FPS)

    # ==============================================
    # EVENTS
    # ==============================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # ------------------------------------------
        # BREAK BLOCK
        # ------------------------------------------

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):

            mouse_x, mouse_y = pygame.mouse.get_pos()

            world_x = mouse_x + camera.camera_x
            world_y = mouse_y + camera.camera_y

            grid_x = int(world_x // BLOCK_SIZE)
            grid_y = int(world_y // BLOCK_SIZE)

            if (
                0 <= grid_x < GRID_WIDTH
                and 0 <= grid_y < GRID_HEIGHT
            ):

                player_grid_x = player.rect.centerx // BLOCK_SIZE
                player_grid_y = player.rect.centery // BLOCK_SIZE

                distance = (
                    (grid_x - player_grid_x) ** 2
                    + (grid_y - player_grid_y) ** 2
                ) ** 0.5

                if (
                    distance <= MINING_RANGE
                    and world[grid_y][grid_x] != "air"
                ):

                    block_type = world[grid_y][grid_x]
                    world[grid_y][grid_x] = "air"

                    drops.append(
                        Drop(grid_x, grid_y, block_type)
                    )

        # ------------------------------------------
        # PLACE BLOCK
        # ------------------------------------------

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 3
        ):

            if (
                selected_item
                and inventory.get(selected_item, 0) > 0
            ):

                mouse_x, mouse_y = pygame.mouse.get_pos()

                world_x = mouse_x + camera.camera_x
                world_y = mouse_y + camera.camera_y

                grid_x = int(world_x // BLOCK_SIZE)
                grid_y = int(world_y // BLOCK_SIZE)

                if (
                    0 <= grid_x < GRID_WIDTH
                    and 0 <= grid_y < GRID_HEIGHT
                ):

                    player_grid_x = player.rect.centerx // BLOCK_SIZE
                    player_grid_y = player.rect.centery // BLOCK_SIZE

                    distance = (
                        (grid_x - player_grid_x) ** 2
                        + (grid_y - player_grid_y) ** 2
                    ) ** 0.5

                    if (
                        distance <= MINING_RANGE
                        and world[grid_y][grid_x] == "air"
                    ):

                        world[grid_y][grid_x] = selected_item
                        inventory[selected_item] -= 1

                        if inventory[selected_item] <= 0:
                            del inventory[selected_item]
                            selected_item = None

        # ------------------------------------------
        # SCROLL INVENTORY
        # ------------------------------------------

        if event.type == pygame.MOUSEWHEEL:

            items = list(inventory.keys())

            if items:

                if selected_item not in items:
                    selected_item = items[0]

                else:
                    index = items.index(selected_item)
                    index = (index + event.y) % len(items)
                    selected_item = items[index]

    # ==============================================
    # UPDATE
    # ==============================================

    # Detect water before swimming input.
    player.update_water_state(world)

    # Player movement.
    player.handle_input()
    player.apply_gravity()
    player.move_and_collide(world)

    # Update oxygen, drowning damage, village healing
    # and potion input.
    player.update_survival(world)
    player.update_combat()

    # Update the active Shore Guardian and process player attacks.
    for crab in crabs[:]:
        crab.update(player, world)
        player.attack_hits_enemy(crab)

        if not crab.alive:
            crabs.remove(crab)
            crabs_defeated += 1
            print(f"SHORE GUARDIANS DEFEATED: {crabs_defeated}/{TOTAL_CRABS}")

            if crabs_defeated < TOTAL_CRABS:
                spawn_next_crab()
            else:
                sea_unlocked = True
                victory_message_timer = 240
                print("THE SEA IS UNLOCKED!")

    if victory_message_timer > 0:
        victory_message_timer -= 1

    # Camera.
    camera.update(player)

    # Update drops.
    for drop in drops:
        drop.update(world)

    # Collect drops.
    for drop in drops[:]:

        if player.rect.colliderect(drop.rect):

            block_type = drop.block_type

            inventory[block_type] = (
                inventory.get(block_type, 0) + 1
            )

            if selected_item is None:
                selected_item = block_type

            drops.remove(drop)

    # ==============================================
    # DRAW BACKGROUND
    # ==============================================

    draw_village_background(screen, camera)

    # ==============================================
    # MOUNTAINS
    # ==============================================

    mountain_x = -camera.camera_x * 0.2

    screen.blit(
        mountains_bg,
        (mountain_x, 0)
    )

    # ==============================================
    # CLOUDS
    # ==============================================

    screen.blit(
        cloud_small,
        (-camera.camera_x * 0.4 + 100, 80)
    )

    screen.blit(
        cloud_medium,
        (-camera.camera_x * 0.35 + 600, 140)
    )

    screen.blit(
        cloud_big,
        (-camera.camera_x * 0.3 + 1200, 60)
    )

    # ==============================================
    # DRAW WORLD
    # ==============================================

    for y in range(GRID_HEIGHT):

        for x in range(GRID_WIDTH):

            block = world[y][x]

            if block == "air":
                continue

            screen_x, screen_y = camera.apply(
                x * BLOCK_SIZE,
                y * BLOCK_SIZE
            )

            if (
                -BLOCK_SIZE < screen_x < WIDTH
                and -BLOCK_SIZE < screen_y < HEIGHT
            ):

                if block in TILES:

                    screen.blit(
                        TILES[block],
                        (screen_x, screen_y)
                    )

                else:

                    pygame.draw.rect(
                        screen,
                        (255, 0, 0),
                        (
                            screen_x,
                            screen_y,
                            BLOCK_SIZE,
                            BLOCK_SIZE
                        )
                    )

    # ==============================================
    # DRAW DROPS
    # ==============================================

    for drop in drops:
        drop.draw(
            screen,
            COLORS,
            camera
        )

    # ==============================================
    # DRAW PLAYER
    # ==============================================

    player.draw(screen, camera)

    # Draw the active crab.
    for crab in crabs:
        crab.draw(screen, camera)

    # Shore Guardian progress.
    if not sea_unlocked:
        if shore_spawn is not None:
            wave_text = wave_font.render(
                f"SHORE GUARDIAN {min(crabs_defeated + 1, TOTAL_CRABS)}/{TOTAL_CRABS}",
                True,
                (255, 255, 255)
            )
            wave_bg = pygame.Surface(
                (wave_text.get_width() + 24, wave_text.get_height() + 14),
                pygame.SRCALPHA
            )
            wave_bg.fill((20, 25, 35, 190))
            screen.blit(wave_bg, (WIDTH // 2 - wave_bg.get_width() // 2, 18))
            screen.blit(
                wave_text,
                (WIDTH // 2 - wave_text.get_width() // 2, 25)
            )

    # Sea-unlocked victory announcement.
    if sea_unlocked and victory_message_timer > 0:
        banner = pygame.Surface((WIDTH, 150), pygame.SRCALPHA)
        banner.fill((5, 25, 45, 215))
        banner_y = HEIGHT // 2 - 75
        screen.blit(banner, (0, banner_y))

        title_text = victory_font.render(
            "THE SEA IS UNLOCKED!",
            True,
            (100, 220, 255)
        )
        subtitle_text = subtitle_font.render(
            "The Shore Guardians have fallen. Explore beyond the shore!",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title_text,
            (WIDTH // 2 - title_text.get_width() // 2, banner_y + 22)
        )
        screen.blit(
            subtitle_text,
            (WIDTH // 2 - subtitle_text.get_width() // 2, banner_y + 88)
        )

    # ==============================================
    # UNDERWATER EFFECT
    # ==============================================

    draw_underwater_overlay(
        screen,
        player,
        camera,
        world
    )

    # ==============================================
    # UI
    # ==============================================

    draw_status(
        screen,
        player,
        selected_item
    )

    draw_health(screen, player)

    draw_oxygen(
        screen,
        player.oxygen / player.max_oxygen
    )

    draw_inventory(
        screen,
        inventory,
        COLORS
    )

    draw_minimap(
        screen,
        world,
        player,
        COLORS
    )

    # Potion counter.
    potion_count = getattr(player, "potions", 0)

    potion_text = font.render(
        f"Potions: {potion_count}  |  Press H to heal",
        True,
        (255, 255, 255)
    )

    screen.blit(
        potion_text,
        (40, HEIGHT - 40)
    )

    # ==============================================
    # DISPLAY
    # ==============================================

    pygame.display.flip()


# ==================================================
# QUIT
# ==================================================

pygame.quit()
