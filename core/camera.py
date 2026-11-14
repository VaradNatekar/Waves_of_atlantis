# core/camera.py

from core.settings import *

class Camera:
    def __init__(self):
        self.section = 0
        self.blocks_per_screen = WIDTH // BLOCK_SIZE

        self.camera_x = 0
        self.camera_y = 0

    def update(self, player):
        # ---------- Horizontal Section Camera ----------
        player_block_x = player.rect.centerx // BLOCK_SIZE
        new_section = player_block_x // self.blocks_per_screen

        total_sections = GRID_WIDTH // self.blocks_per_screen
        max_section = total_sections - 1

        new_section = max(0, min(new_section, max_section))

        self.section = new_section
        self.camera_x = self.section * WIDTH

        # ---------- Vertical Follow Camera ----------
        self.camera_y = int(player.rect.centery - HEIGHT // 2)

        # Clamp vertically
        max_camera_y = GRID_HEIGHT * BLOCK_SIZE - HEIGHT
        self.camera_y = max(0, min(self.camera_y, max_camera_y))

    def apply(self, x, y):
     return int(x - self.camera_x), int(y - self.camera_y)
