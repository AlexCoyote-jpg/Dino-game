import pygame
import time
from functools import lru_cache

class ResponsiveScalerDinamico:
    """
    Escalador responsivo que ajusta su base dinámicamente según el último tamaño.
    Ideal para aplicaciones en las que la interfaz debe adaptarse suavemente a cambios de ventana.
    """
    def __init__(self, initial_width=None, initial_height=None, uniform=False):
        info = pygame.display.Info()
        self.base_width = initial_width or info.current_w
        self.base_height = initial_height or info.current_h
        self.uniform = uniform

        self.current_width = self.base_width
        self.current_height = self.base_height
        self._scale_x = 1.0
        self._scale_y = 1.0
        self._scale_avg = 1.0
        self.last_update_time = time.time()

        self._update_scales()

    def update(self, new_width: int, new_height: int) -> bool:
        """Actualiza dimensiones, recalcula escalas y redefine la base."""
        if (new_width, new_height) == (self.current_width, self.current_height):
            return False

        # Establecer la base anterior como referencia
        self.base_width = self.current_width
        self.base_height = self.current_height

        self.current_width = new_width
        self.current_height = new_height

        self._update_scales()
        self.clear_cache()
        return True

    def _update_scales(self):
        self._scale_x = self.current_width / self.base_width
        self._scale_y = self.current_height / self.base_height
        if self.uniform:
            avg = (self._scale_x + self._scale_y) / 2
            self._scale_x = self._scale_y = avg
        self._scale_avg = self._scale_x * 0.6 + self._scale_y * 0.4

    def clear_cache(self):
        self.sx.cache_clear()
        self.sy.cache_clear()
        self.sf.cache_clear()

    @lru_cache(maxsize=1024)
    def sx(self, value):
        return int(value * self._scale_x)

    @lru_cache(maxsize=1024)
    def sy(self, value):
        return int(value * self._scale_y)

    @lru_cache(maxsize=512)
    def sf(self, size):
        return max(12, int(size * self._scale_avg))

    def scale_rect(self, x, y, w, h):
        return self.sx(x), self.sy(y), self.sx(w), self.sy(h)

    def get_centered_rect(self, w, h, vertical_offset=0, horizontal_offset=0):
        sw = self.sx(w)
        sh = self.sy(h)
        cx = (self.current_width - sw) // 2 + self.sx(horizontal_offset)
        cy = (self.current_height - sh) // 2 + self.sy(vertical_offset)
        return cx, cy, sw, sh

    def maintain_aspect_ratio(self, width, height):
        ratio = width / height
        current_ratio = self.current_width / self.current_height
        if ratio > current_ratio:
            new_height = self.sy(height)
            new_width = int(new_height * ratio)
        else:
            new_width = self.sx(width)
            new_height = int(new_width / ratio)
        return new_width, new_height
