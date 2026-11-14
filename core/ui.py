
import pygame
from core.settings import *

# ================= HUD CONFIG =================

HUD_BG = (10, 20, 30, 210)
HUD_BORDER = (0, 180, 200)
HUD_TEXT = (220, 255, 255)

FONT = pygame.font.SysFont("courier", 16, bold=True)
SMALL_FONT = pygame.font.SysFont("courier", 14, bold=True)


# ================= PANEL =================

def draw_panel(surface, rect):
    panel = pygame.Surface(
        (rect.width, rect.height),
        pygame.SRCALPHA
    )

    panel.fill(HUD_BG)
    pygame.draw.rect(panel, HUD_BORDER, panel.get_rect(), 2)
    surface.blit(panel, (rect.x, rect.y))


# ================= STATUS =================

def draw_status(surface, player, selected_item):
    panel_rect = pygame.Rect(20, 20, 340, 110)
    draw_panel(surface, panel_rect)

    grid_x = player.rect.centerx // BLOCK_SIZE
    grid_y = player.rect.centery // BLOCK_SIZE

    lines = [
        f"POS: [X:{grid_x:03} Y:{grid_y:03}]",
        f"ACTIVE TOOL: {selected_item.upper() if selected_item else 'NONE'}",
        f"SELECTED: {selected_item.upper() if selected_item else 'NONE'}"
    ]

    for i, line in enumerate(lines):
        text = FONT.render(line, True, HUD_TEXT)
        surface.blit(text, (35, 35 + i * 28))


# ================= COMPACT HEALTH BAR =================

def draw_health(surface, player):

    x = 40
    y = 155

    width = 180
    height = 10

    health = max(0, min(player.health, player.max_health))
    percentage = health / player.max_health if player.max_health else 0

    label = SMALL_FONT.render(
        f"HP {health}/{player.max_health}",
        True,
        HUD_TEXT
    )

    surface.blit(label, (x, y - 19))

    pygame.draw.rect(
        surface,
        (35, 35, 35),
        (x, y, width, height),
        border_radius=5
    )

    if percentage > 0:
        pygame.draw.rect(
            surface,
            (220, 40, 40),
            (x, y, int(width * percentage), height),
            border_radius=5
        )

    pygame.draw.rect(
        surface,
        (180, 190, 200),
        (x, y, width, height),
        1,
        border_radius=5
    )


# ================= COMPACT OXYGEN BAR =================

def draw_oxygen(surface, oxygen_percent):

    x = 40
    y = 195

    width = 180
    height = 10

    oxygen_percent = max(0, min(1, oxygen_percent))

    label = SMALL_FONT.render(
        f"O2 {int(oxygen_percent * 100)}%",
        True,
        HUD_TEXT
    )

    surface.blit(label, (x, y - 19))

    pygame.draw.rect(
        surface,
        (35, 35, 35),
        (x, y, width, height),
        border_radius=5
    )

    if oxygen_percent > 0:
        pygame.draw.rect(
            surface,
            (0, 150, 255),
            (x, y, int(width * oxygen_percent), height),
            border_radius=5
        )

    pygame.draw.rect(
        surface,
        (180, 190, 200),
        (x, y, width, height),
        1,
        border_radius=5
    )


# ================= INVENTORY =================

def draw_inventory(surface, inventory, COLORS):

    items = list(inventory.items())

    slot_size = 60
    spacing = 15

    total_width = len(items) * (slot_size + spacing)

    start_x = (WIDTH - total_width) // 2
    y = HEIGHT - 80

    for i, (item, count) in enumerate(items):

        x = start_x + i * (slot_size + spacing)

        pygame.draw.rect(
            surface,
            (20, 30, 40),
            (x, y, slot_size, slot_size)
        )

        pygame.draw.rect(
            surface,
            HUD_BORDER,
            (x, y, slot_size, slot_size),
            2
        )

        color = COLORS.get(item, (150, 150, 150))

        pygame.draw.rect(
            surface,
            color,
            (x + 15, y + 15, 30, 30)
        )

        text = SMALL_FONT.render(str(count), True, HUD_TEXT)
        surface.blit(text, (x + 5, y + 5))


# ================= MINIMAP =================

def draw_minimap(surface, world, player, colors):

    map_width = 140
    scale = map_width / (GRID_WIDTH * BLOCK_SIZE)

    map_height = int(GRID_HEIGHT * BLOCK_SIZE * scale)

    map_x = WIDTH - map_width - 20
    map_y = 20

    draw_panel(
        surface,
        pygame.Rect(map_x, map_y, map_width, map_height)
    )

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):

            block = world[y][x]

            if block != "air":

                color = colors.get(block, (100, 100, 100))

                bx = map_x + int(x * BLOCK_SIZE * scale)
                by = map_y + int(y * BLOCK_SIZE * scale)

                size = max(2, int(BLOCK_SIZE * scale))

                pygame.draw.rect(
                    surface,
                    color,
                    (bx, by, size, size)
                )

    px = map_x + int(player.rect.centerx * scale)
    py = map_y + int(player.rect.centery * scale)

    pygame.draw.circle(
        surface,
        (255, 0, 0),
        (px, py),
        3
    )
