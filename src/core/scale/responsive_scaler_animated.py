# core/responsive_scaler_animated.py

import pygame
import time
from functools import lru_cache

class ResponsiveScalerAnimado:
    def __init__(self, initial_width=None, initial_height=None, uniform=False, transition_speed=6.0):
        info = pygame.display.Info()
        self.current_width = initial_width or info.current_w
        self.current_height = initial_height or info.current_h
        self.target_width = self.current_width
        self.target_height = self.current_height
        self.base_width = self.current_width
        self.base_height = self.current_height
        self.uniform = uniform
        self.transition_speed = transition_speed
        self._scale_x = 1.0
        self._scale_y = 1.0
        self._scale_avg = 1.0
        self.last_time = time.time()
        self._update_scales()

    def update(self, new_width, new_height):
        self.target_width = new_width
        self.target_height = new_height

    def tick(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        t = min(dt * self.transition_speed, 1.0)
        self.current_width += (self.target_width - self.current_width) * t
        self.current_height += (self.target_height - self.current_height) * t
        self._update_scales()
        self.clear_cache()

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
        cx = (int(self.current_width) - sw) // 2 + self.sx(horizontal_offset)
        cy = (int(self.current_height) - sh) // 2 + self.sy(vertical_offset)
        return cx, cy, sw, sh
