# navigation_bar.py
import pygame
import os
from functools import lru_cache
from .components.utils import Boton, TooltipManager
from .animations import get_surface

class NavigationBar:
    def __init__(self, options, down=True, icons=None, tooltips=None):
        self.options = options
        self.selected = 0
        self.down = down
        self._anim_sizes = [0.0 for _ in options]
        self._anim_opacity = [1.0 for _ in options]
        self.botones = []
        self.icons = icons or [None] * len(options)
        self.tooltips = tooltips or [None] * len(options)
        self._tooltip_idx = None
        self._tooltip_alpha = 0
        self.tooltip_manager = TooltipManager(delay=1.0)

    def get_height(self):
        alto = pygame.display.get_surface().get_height() if pygame.display.get_surface() else 700
        return max(36, min(60, int(alto * 0.07))) + max(6, int(alto * 0.01)) * 2

    @staticmethod
    @lru_cache(maxsize=16)
    def get_cached_font(font_path, font_size):
        try:
            return pygame.font.Font(font_path, font_size)
        except Exception:
            return pygame.font.SysFont("Segoe UI", font_size, bold=True)

    @staticmethod
    @lru_cache(maxsize=64)
    def get_cached_icon(icon_id, icon_bytes, size):
        # icon_id: unique identifier for the icon (e.g., id(icon) or a string)
        # icon_bytes: bytes of the icon surface for cache key uniqueness
        surf = pygame.image.frombuffer(icon_bytes, (size, size), "RGBA")
        return pygame.transform.smoothscale(surf, (size, size))

    def draw(self, surface, logo=None, logo_height=None):
        ancho, alto = surface.get_size()
        num = len(self.options)

        # Responsividad: tamaño de fuente y botones
        b_alto = max(36, min(60, int(alto * 0.07)))
        b_ancho = max(90, min(180, int(ancho * 0.12)))
        b_ancho_sel = int(b_ancho * 1.15)
        b_alto_sel = int(b_alto * 1.15)
        sep = max(2, int(b_ancho * 0.04))
        radius = max(24, int(b_alto * 0.48))
        margin_y = max(20, int(alto * 0.04))
        margin_x = max(18, int(ancho * 0.03))
        logo_margin = max(4, int(ancho * 0.005))

        # --- Calcular ancho total del navbar ---
        bar_w = (num - 1) * sep
        for i in range(num):
            bar_w += b_ancho_sel if i == self.selected else b_ancho

        # --- Centrar el navbar en la pantalla ---
        bar_x = (ancho - bar_w) // 2
        bar_y = margin_y

        # --- Si hay logo, colócalo a la izquierda del navbar, ajustando si se solapan ---
        lw = lh = lmy = 0
        logo_x = margin_x
        if logo:
            lw0, lh0 = logo.get_size()
            lw = int(min(int(ancho * 0.20), lw0))
            max_lh = int(alto * 0.25 if logo_height is None else min(alto * 0.25, logo_height))
            scale = min(lw / lw0, max_lh / lh0, 1.5)
            lw = int(lw0 * scale)
            lh = int(lh0 * scale)
            lmy = max(6, (b_alto - lh) // 2 + margin_y)
            logo_x = bar_x - lw - logo_margin
            # Si el logo se sale de pantalla, lo pegamos al margen
            if logo_x < margin_x:
                logo_x = margin_x
                bar_x = logo_x + lw + logo_margin

        # Sombra pegada a los botones (sin espacio)
        pad_x, pad_y = 0, 0
        sombra = get_surface(bar_w + pad_x * 2, b_alto + pad_y * 2, alpha=True)
        pygame.draw.rect(sombra, (0, 0, 0, 32), sombra.get_rect(), border_radius=radius + 10)
        surface.blit(sombra, (bar_x - pad_x, bar_y - pad_y))

        # Dibuja el logo si existe
        if logo:
            logo_scaled = pygame.transform.smoothscale(logo, (lw, lh))
            surface.blit(logo_scaled, (logo_x, lmy))

        # Fuente San Francisco Pro Text Bold o fallback (cacheada)
        font_size = int(b_alto * 0.55)
        sf_font_path = os.path.join("assets", "fuentes", "San Francisco Pro Text", "SFProText-Bold.ttf")
        fuente = self.get_cached_font(sf_font_path, font_size)

        colores = [
            ((33, 150, 243), (3, 169, 244)),      # Azul vivo
            ((76, 175, 80), (139, 195, 74)),      # Verde vivo
            ((255, 193, 7), (255, 152, 0)),       # Amarillo/Naranja vivo
            ((244, 67, 54), (233, 30, 99)),       # Rojo/Rosa vivo
            ((156, 39, 176), (103, 58, 183)),     # Púrpura/Indigo vivo
        ]
        txt_color_sel = (30, 30, 50)
        txt_color_unsel = (255, 255, 255)
        anim_speed = 0.22
        opacity_speed = 0.18

        mouse_pos = pygame.mouse.get_pos()
        self._tooltip_idx = None

        # Actualiza el TooltipManager para la barra de navegación
        self.tooltip_manager.active_elements.clear()

        # Animaciones
        for i in range(num):
            tgt = 1.0 if i == self.selected else 0.0
            self._anim_sizes[i] += (tgt - self._anim_sizes[i]) * anim_speed
            tgt_op = 1.0 if i == self.selected else 0.5
            self._anim_opacity[i] += (tgt_op - self._anim_opacity[i]) * opacity_speed

        self.botones.clear()
        x = bar_x

        for i, txt in enumerate(self.options):
            a = min(1.0, max(0.0, self._anim_sizes[i]))
            ancho = int(b_ancho + (b_ancho_sel - b_ancho) * a)
            alto = int(b_alto + (b_alto_sel - b_alto) * a)
            y = bar_y + (b_alto - alto) // 2
            icon = self.icons[i] if i < len(self.icons) else None
            if i == self.selected:
                color_top, color_bottom = colores[i % len(colores)]
                color_texto = txt_color_sel
                #border_color = (68, 68, 78, 32)  # Sombra muy ligera
                border_color = False
                estilo = "apple"
                text_alpha = 255
            else:
                color_top = color_bottom = (0, 0, 0, 0)
                color_texto = txt_color_unsel
                border_color = False
                estilo = "flat"
                text_alpha = int(255 * self._anim_opacity[i])
            boton = Boton(
                txt, x, y, ancho, alto,
                color_texto=color_texto, fuente=fuente,
                border_radius=radius, estilo=estilo,
                color_top=color_top, color_bottom=color_bottom,
                border_color=border_color,
                texto_visible=True,
                tooltip=self.tooltips[i] if i < len(self.tooltips) else None
            )
            # Soporte para iconos: dibuja el icono si existe (cacheado)
            if icon:
                icon_size = int(alto * 0.6)
                icon_bytes = pygame.image.tostring(icon, "RGBA")
                icon_img = self.get_cached_icon(id(icon), icon_bytes, icon_size)
                icon_x = x + (ancho - icon_size) // 2
                icon_y = y + (alto - icon_size) // 2 - (font_size // 3)
                surface.blit(icon_img, (icon_x, icon_y))
                boton.texto_espaciado = icon_size // 4

            # Animación de opacidad en el texto
            if boton.texto and not i == self.selected:
                text_surf = fuente.render(boton.texto, True, color_texto)
                text_surf.set_alpha(text_alpha)
                text_rect = text_surf.get_rect(center=(x + ancho // 2, y + alto // 2))
                surface.blit(text_surf, text_rect)
            else:
                boton.draw(surface, self.tooltip_manager)

            self.botones.append(boton)
            if boton.tooltip:
                self.tooltip_manager.register(f"navbar_{i}", boton.tooltip, boton.rect)
            x += ancho + sep

        # Dibuja el tooltip usando TooltipManager
        self.tooltip_manager.update(mouse_pos)
        self.tooltip_manager.draw(surface)

    def handle_event(self, event, logo=None, logo_height=None):
        #if event.type == pygame.KEYDOWN:
            #if event.key == pygame.K_LEFT:
                #self.selected = (self.selected - 1) % len(self.options)
                #return self.selected
            #elif event.key == pygame.K_RIGHT:
                #self.selected = (self.selected + 1) % len(self.options)
                #return self.selected
            #elif event.key == pygame.K_RETURN:
                #return self.selected
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for idx, boton in enumerate(self.botones):
                if boton.collidepoint(mouse_pos):
                    self.selected = idx
                    return self.selected
        return None
