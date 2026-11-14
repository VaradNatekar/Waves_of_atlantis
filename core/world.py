
import random
from core.settings import *


# ==========================================
# SAFE ZONE
# ==========================================

VILLAGE_START = 0
VILLAGE_END = BLOCKS_PER_SCREEN


def is_safe_zone(world_x):
    tile_x = int(world_x // BLOCK_SIZE)
    return VILLAGE_START <= tile_x < VILLAGE_END


# ==========================================
# WORLD HELPERS
# ==========================================

def place_block(world, x, y, block):
    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
        world[y][x] = block


def get_surface_height(x):
    return BASE_GROUND_HEIGHT


# ==========================================
# SHORE GENERATION
# ==========================================

def get_shore_height(distance):
    if distance < 8:
        return BASE_GROUND_HEIGHT + 1

    elif distance < 14:
        return BASE_GROUND_HEIGHT + 2

    elif distance < 20:
        return BASE_GROUND_HEIGHT + 4

    elif distance < 25:
        return BASE_GROUND_HEIGHT + 7

    else:
        return BASE_GROUND_HEIGHT + 9


def generate_shore(world, x, distance):

    ground_height = get_shore_height(distance)
    water_level = BASE_GROUND_HEIGHT + 4

    for y in range(GRID_HEIGHT):

        # Air above the beach and ocean
        if y < min(ground_height, water_level):
            world[y][x] = "air"

        # Water above underwater terrain
        elif water_level <= y < ground_height:
            world[y][x] = "water"

        # Beach surface
        elif y == ground_height:

            if distance < 14:
                world[y][x] = "sand"

            else:
                world[y][x] = "wet_sand"

        # Sandy underwater seabed
        elif y <= ground_height + SOIL_DEPTH:
            world[y][x] = "sand"

        # Deep underground
        else:
            world[y][x] = "stone"


# ==========================================
# WORLD GENERATION
# ==========================================

def generate_world():

    world = [
        ["air" for _ in range(GRID_WIDTH)]
        for _ in range(GRID_HEIGHT)
    ]

    for x in range(GRID_WIDTH):

        section = x // BLOCKS_PER_SCREEN

        # ----------------------------------
        # SAFE VILLAGE TERRAIN
        # ----------------------------------

        if section == 0:

            ground_height = BASE_GROUND_HEIGHT

            for y in range(GRID_HEIGHT):

                if y < ground_height:
                    world[y][x] = "air"

                elif y == ground_height:
                    world[y][x] = "grass"

                elif y <= ground_height + SOIL_DEPTH:
                    world[y][x] = "soil"

                else:
                    world[y][x] = "stone"

        # ----------------------------------
        # BEACH AND OCEAN
        # ----------------------------------

        elif section == 1:

            distance = x - BLOCKS_PER_SCREEN

            generate_shore(world, x, distance)

        # ----------------------------------
        # OTHER WORLD SECTIONS
        # ----------------------------------

        else:

            ground_height = BASE_GROUND_HEIGHT
            ground_height += random.choice([-1, 0, 1])

            ground_height = max(
                5,
                min(ground_height, GRID_HEIGHT - 10)
            )

            for y in range(GRID_HEIGHT):

                if y < ground_height:
                    world[y][x] = "air"

                elif y == ground_height:
                    world[y][x] = "grass"

                elif y <= ground_height + SOIL_DEPTH:
                    world[y][x] = "soil"

                else:
                    world[y][x] = "stone"

    return world


# ==========================================
# DEPTH SYSTEM
# ==========================================

def get_depth_level(player):

    grid_y = player.rect.centery // BLOCK_SIZE

    if grid_y < GRID_HEIGHT * 0.25:
        return "surface"

    elif grid_y < GRID_HEIGHT * 0.5:
        return "underground"

    elif grid_y < GRID_HEIGHT * 0.75:
        return "deep"

    else:
        return "abyss"
