import pygame
import time
from functools import lru_cache
from typing import Optional, Tuple, Dict, Any

# --- Memory Management & Caching ---
FUENTE_NOMBRE = "Segoe UI"

@lru_cache(maxsize=8)
def get_default_font() -> pygame.font.Font:
    """Devuelve la fuente por defecto, cacheada."""
    if not pygame.font.get_init():
        pygame.font.init()
    return pygame.font.SysFont(FUENTE_NOMBRE, 28)

@lru_cache(maxsize=32)
def obtener_fuente(tamaño: int, negrita: bool = False) -> pygame.font.Font:
    """Obtiene una fuente cacheada por tamaño y negrita."""
    if not pygame.font.get_init():
        pygame.font.init()
    return pygame.font.SysFont(FUENTE_NOMBRE, tamaño, bold=negrita)

@lru_cache(maxsize=128)
def render_text_cached(text: str, size: int, bold: bool, color: Tuple[int, int, int]) -> pygame.Surface:
    """Renderiza texto y lo cachea para mejorar el rendimiento."""
    font = obtener_fuente(size, bold)
    return font.render(text, True, color)

@lru_cache(maxsize=32)
def get_gradient(ancho: int, alto: int, color_top: Tuple[int, int, int], color_bottom: Tuple[int, int, int]) -> pygame.Surface:
    """Genera y cachea un gradiente vertical."""
    grad = pygame.Surface((1, alto), pygame.SRCALPHA)
    for i in range(alto):
        ratio = i / (alto - 1) if alto > 1 else 0
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        grad.set_at((0, i), (r, g, b, 255))
    return pygame.transform.scale(grad, (ancho, alto))

# --- Dirty Rectangles for Partial Updates ---
DIRTY_RECTS = []

def mark_dirty(rect: pygame.Rect):
    DIRTY_RECTS.append(rect)

def get_dirty_rects():
    rects = DIRTY_RECTS.copy()
    DIRTY_RECTS.clear()
    return rects

# --- Boton Class ---
class Boton_Images:
    """
    Botón avanzado con soporte para imágenes, personalización de posición de imagen, texto, colores,
    bordes, radios, estilos y optimización de renderizado.
    """
    def __init__(
        self,
        texto: str,
        x: int,
        y: int,
        ancho: int,
        alto: int,
        imagen: Optional[pygame.Surface] = None,
        imagen_pos: str = "left",  # "left", "right", "top", "bottom", "center"
        imagen_padding: int = 8,
        imagen_alpha: Optional[int] = None,
        color_normal: Tuple[int, int, int] = (220, 230, 245),
        color_hover: Optional[Tuple[int, int, int]] = None,
        color_texto: Tuple[int, int, int] = (30, 30, 30),
        fuente: Optional[pygame.font.Font] = None,
        fuente_size: Optional[int] = None,
        texto_negrita: bool = False,
        texto_cursiva: bool = False,
        texto_subrayado: bool = False,
        texto_espaciado: int = 0,
        texto_visible: bool = True,
        texto_alineacion: str = "center",  # "left", "center", "right"
        border_radius: int = 12,
        estilo: str = "apple",  # "apple", "flat", "round"
        color_top: Optional[Tuple[int, int, int]] = None,
        color_bottom: Optional[Tuple[int, int, int]] = None,
        border_color: Optional[Tuple[int, int, int, int]] = None,
        border_width: int = 2,
        padding: int = 12,
        texto_centrado: bool = True,
        texto_adaptativo: bool = False,
    ):
        self.texto = texto
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.imagen = imagen
        self.imagen_pos = imagen_pos
        self.imagen_padding = imagen_padding
        self.imagen_alpha = imagen_alpha
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.color_texto = color_texto
        self.fuente = fuente or obtener_fuente(fuente_size or 20, texto_negrita)
        self.fuente.set_bold(texto_negrita)
        self.fuente.set_italic(texto_cursiva)
        self.fuente.set_underline(texto_subrayado)
        self.texto_espaciado = texto_espaciado
        self.texto_visible = texto_visible
        self.texto_alineacion = texto_alineacion
        self.border_radius = border_radius
        self.estilo = estilo
        self.color_top = color_top or (90, 180, 255)
        self.color_bottom = color_bottom or (0, 120, 255)
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.border_color = (255, 255, 255, 90) if border_color is True else border_color
        self.border_width = border_width
        self.padding = padding
        self.texto_centrado = texto_centrado
        self.texto_adaptativo = texto_adaptativo
        self._shadow_surf = self._make_shadow()
        self._gradiente_cache = None
        self._last_hovered = None

    def _make_shadow(self):
        shadow_offset = 3
        shadow_rect = pygame.Rect(self.x - 3, self.y - 3, self.ancho + 6, self.alto + 6)
        shadow_surf = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surf, (0, 0, 0, 38),
            (shadow_offset, shadow_offset, self.ancho, self.alto),
            border_radius=self.border_radius + 4
        )
        return shadow_surf

    def draw(self, pantalla):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        if self.estilo == "apple":
            self._draw_apple(pantalla, hovered)
        elif self.estilo == "round":
            self._draw_round(pantalla, hovered)
        else:
            self._draw_flat(pantalla, hovered)
        mark_dirty(self.rect)

    def _draw_apple(self, pantalla, hovered):
        pantalla.blit(self._shadow_surf, (self.x - 3, self.y - 3))
        color_top = self.color_hover if hovered and self.color_hover else self.color_top
        color_bottom = self.color_hover if hovered and self.color_hover else self.color_bottom

        gradiente = get_gradient(self.ancho, self.alto, color_top, color_bottom)
        mask = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, self.ancho, self.alto), border_radius=self.border_radius)
        gradiente = gradiente.copy()
        gradiente.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pantalla.blit(gradiente, (self.x, self.y))

        if self.border_color and self.border_width > 0:
            pygame.draw.rect(
                pantalla, self.border_color,
                (self.x, self.y, self.ancho, self.alto),
                width=self.border_width, border_radius=self.border_radius
            )

        self._draw_content(pantalla)

    def _draw_flat(self, pantalla, hovered):
        color = self.color_hover if hovered and self.color_hover else self.color_normal
        pygame.draw.rect(pantalla, color, self.rect, border_radius=self.border_radius)
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(
                pantalla, self.border_color,
                (self.x, self.y, self.ancho, self.alto),
                width=self.border_width, border_radius=self.border_radius
            )
        self._draw_content(pantalla)

    def _draw_round(self, pantalla, hovered):
        color = self.color_hover if hovered and self.color_hover else self.color_normal
        radius = min(self.ancho, self.alto) // 2
        center = (self.x + self.ancho // 2, self.y + self.alto // 2)
        pygame.draw.circle(pantalla, color, center, radius)
        if self.border_color and self.border_width > 0:
            pygame.draw.circle(
                pantalla, self.border_color, center, radius, width=self.border_width
            )
        self._draw_content(pantalla, round_mode=True)

    def _draw_content(self, pantalla, round_mode=False):
        area = self.rect.inflate(-2 * self.padding, -2 * self.padding)
        img = self.imagen
        if img and self.imagen_alpha is not None:
            img = img.copy()
            img.set_alpha(self.imagen_alpha)
        img_rect = img.get_rect() if img else pygame.Rect(0, 0, 0, 0)

        # Layout imagen
        if img:
            if self.imagen_pos == "left":
                img_rect.topleft = (area.x, area.y + (area.height - img_rect.height) // 2)
            elif self.imagen_pos == "right":
                img_rect.topright = (area.right, area.y + (area.height - img_rect.height) // 2)
            elif self.imagen_pos == "top":
                img_rect.midtop = (area.centerx, area.y)
            elif self.imagen_pos == "bottom":
                img_rect.midbottom = (area.centerx, area.bottom)
            elif self.imagen_pos == "center":
                img_rect.center = area.center
            else:
                img_rect.topleft = (area.x, area.y)
            pantalla.blit(img, img_rect)

        # Layout texto
        if self.texto_visible and self.texto:
            text_area_x = area.x
            text_area_y = area.y
            text_area_w = area.width
            text_area_h = area.height

            # Ajusta área de texto si hay imagen a izquierda/derecha
            if img and self.imagen_pos in ("left", "right"):
                img_w = img_rect.width + self.imagen_padding
                if self.imagen_pos == "left":
                    text_area_x += img_w
                    text_area_w -= img_w
                else:
                    text_area_w -= img_w

            if self.texto_adaptativo:
                mostrar_texto_adaptativo(
                    pantalla, self.texto,
                    text_area_x, text_area_y, text_area_w, text_area_h,
                    self.fuente, self.color_texto,
                    centrado=(self.texto_alineacion == "center")
                )
            else:
                lines = self.texto.split('\n')
                text_surfs = [self.fuente.render(line, True, self.color_texto) for line in lines]
                text_height = sum(s.get_height() + self.texto_espaciado for s in text_surfs) - self.texto_espaciado
                if self.texto_alineacion == "center":
                    txt_x = text_area_x + (text_area_w - max((s.get_width() for s in text_surfs), default=0)) // 2
                elif self.texto_alineacion == "right":
                    txt_x = text_area_x + text_area_w - max((s.get_width() for s in text_surfs), default=0)
                else:  # left
                    txt_x = text_area_x
                txt_y = text_area_y + (text_area_h - text_height) // 2

                y_offset = 0
                for surf in text_surfs:
                    pantalla.blit(surf, (txt_x, txt_y + y_offset))
                    y_offset += surf.get_height() + self.texto_espaciado

    def collidepoint(self, pos):
        if self.estilo == "round":
            center = (self.x + self.ancho // 2, self.y + self.alto // 2)
            radius = min(self.ancho, self.alto) // 2
            return (pos[0] - center[0]) ** 2 + (pos[1] - center[1]) ** 2 <= radius ** 2
        return self.rect.collidepoint(pos)

class Boton:
    def __init__(
        self, texto, x, y, ancho, alto,
        color_normal=(220, 230, 245), color_hover=None,
        color_texto=(30, 30, 30), fuente=None,
        border_radius=12, estilo="apple",
        color_top=None, color_bottom=None,
        border_color: Optional[Tuple[int, int, int, int]] = None,
        border_width: int = 2,
        texto_visible: bool = True,
        texto_espaciado: int = 0,
        texto_adaptativo: bool = True,
    ):
        self.texto = texto
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.color_texto = color_texto
        self.fuente = fuente or get_default_font()
        self.border_radius = border_radius
        self.estilo = estilo
        self.color_top = color_top or (90, 180, 255)
        self.color_bottom = color_bottom or (0, 120, 255)
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.border_color = (255, 255, 255, 90) if border_color is True else border_color
        self.border_width = border_width
        self.texto_visible = texto_visible
        self.texto_espaciado = texto_espaciado
        self.texto_adaptativo = texto_adaptativo
        self._gradiente_cache = None
        self._last_hovered = None
        self._shadow_surf = self._make_shadow()

    def _make_shadow(self):
        shadow_offset = 3
        shadow_rect = pygame.Rect(self.x - 3, self.y - 3, self.ancho + 6, self.alto + 6)
        shadow_surf = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surf, (0, 0, 0, 38),
            (shadow_offset, shadow_offset, self.ancho, self.alto),
            border_radius=self.border_radius + 4
        )
        return shadow_surf

    def draw(self, pantalla):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        if self.estilo == "apple":
            self._draw_apple(pantalla, hovered)
        elif self.estilo == "round":
            self._draw_round(pantalla, hovered)
        else:
            self._draw_flat(pantalla, hovered)
        mark_dirty(self.rect)

    def _draw_apple(self, pantalla, hovered):
        pantalla.blit(self._shadow_surf, (self.x - 3, self.y - 3))
        color_top = self.color_hover if hovered and self.color_hover else self.color_top
        color_bottom = self.color_hover if hovered and self.color_hover else self.color_bottom

        gradiente = get_gradient(self.ancho, self.alto, color_top, color_bottom)
        mask = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, self.ancho, self.alto), border_radius=self.border_radius)
        gradiente = gradiente.copy()
        gradiente.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pantalla.blit(gradiente, (self.x, self.y))

        if self.border_color and self.border_width > 0:
            pygame.draw.rect(
                pantalla, self.border_color,
                (self.x, self.y, self.ancho, self.alto),
                width=self.border_width, border_radius=self.border_radius
            )

        if self.texto_visible and self.texto:
            if self.texto_adaptativo:
                mostrar_texto_adaptativo(
                    pantalla, self.texto, self.x, self.y, self.ancho, self.alto,
                    self.fuente, self.color_texto, centrado=True
                )
            else:
                lines = self.texto.split('\n')
                text_surfs = [self.fuente.render(line, True, self.color_texto) for line in lines]
                text_height = sum(s.get_height() + self.texto_espaciado for s in text_surfs) - self.texto_espaciado
                txt_x = self.x + (self.ancho - max((s.get_width() for s in text_surfs), default=0)) // 2
                txt_y = self.y + (self.alto - text_height) // 2
                y_offset = 0
                for surf in text_surfs:
                    pantalla.blit(surf, (txt_x, txt_y + y_offset))
                    y_offset += surf.get_height() + self.texto_espaciado

    def _draw_flat(self, pantalla, hovered):
        color = self.color_hover if hovered and self.color_hover else self.color_normal
        pygame.draw.rect(pantalla, color, self.rect, border_radius=self.border_radius)
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(
                pantalla, self.border_color,
                (self.x, self.y, self.ancho, self.alto),
                width=self.border_width, border_radius=self.border_radius
            )
        if self.texto_visible and self.texto:
            lines = self.texto.split('\n')
            text_surfs = [self.fuente.render(line, True, self.color_texto) for line in lines]
            text_height = sum(s.get_height() + self.texto_espaciado for s in text_surfs) - self.texto_espaciado
            txt_x = self.x + (self.ancho - max((s.get_width() for s in text_surfs), default=0)) // 2
            txt_y = self.y + (self.alto - text_height) // 2
            y_offset = 0
            for surf in text_surfs:
                pantalla.blit(surf, (txt_x, txt_y + y_offset))
                y_offset += surf.get_height() + self.texto_espaciado

    def _draw_round(self, pantalla, hovered):
        color = self.color_hover if hovered and self.color_hover else self.color_normal
        radius = min(self.ancho, self.alto) // 2
        center = (self.x + self.ancho // 2, self.y + self.alto // 2)
        pygame.draw.circle(pantalla, color, center, radius)
        if self.border_color and self.border_width > 0:
            pygame.draw.circle(
                pantalla, self.border_color, center, radius, width=self.border_width
            )
        if self.texto_visible and self.texto:
            lines = self.texto.split('\n')
            text_surfs = [self.fuente.render(line, True, self.color_texto) for line in lines]
            text_height = sum(s.get_height() + self.texto_espaciado for s in text_surfs) - self.texto_espaciado
            txt_x = self.x + (self.ancho - max((s.get_width() for s in text_surfs), default=0)) // 2
            txt_y = self.y + (self.alto - text_height) // 2
            y_offset = 0
            for surf in text_surfs:
                pantalla.blit(surf, (txt_x, txt_y + y_offset))
                y_offset += surf.get_height() + self.texto_espaciado

    def collidepoint(self, pos):
        if self.estilo == "round":
            center = (self.x + self.ancho // 2, self.y + self.alto // 2)
            radius = min(self.ancho, self.alto) // 2
            return (pos[0] - center[0]) ** 2 + (pos[1] - center[1]) ** 2 <= radius ** 2
        return self.rect.collidepoint(pos)

# --- Adaptive Text Rendering with LRU Cache ---
@lru_cache(maxsize=128)
def _get_lines(texto: str, w: int, font_size: int, bold: bool) -> Tuple[str, ...]:
    fuente = obtener_fuente(font_size, bold)
    parrafos = texto.split('\n\n')
    lines = []
    for parrafo in parrafos:
        for raw_line in parrafo.split('\n'):
            words = raw_line.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                if fuente.size(test_line)[0] <= w:
                    line = test_line
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)
        if parrafo != parrafos[-1]:
            lines.append("")
    return tuple(lines)

def mostrar_texto_adaptativo(
    pantalla: pygame.Surface,
    texto: str,
    x: int,
    y: int,
    w: int,
    h: int,
    fuente_base: Optional[pygame.font.Font] = None,
    color: Tuple[int, int, int] = (30, 30, 30),
    centrado: bool = False
):
    fuente_base = fuente_base or get_default_font()
    max_font_size = fuente_base.get_height()
    min_font_size = 12
    bold = fuente_base.get_bold()

    # Optimized binary search for font size
    left, right = min_font_size, max_font_size
    best_size = min_font_size
    best_lines = ()
    while left <= right:
        mid = (left + right) // 2
        lines = _get_lines(texto, w, mid, bold)
        total_height = len(lines) * obtener_fuente(mid, bold).get_height()
        if total_height <= h:
            best_size = mid
            best_lines = lines
            left = mid + 1
        else:
            right = mid - 1

    fuente = obtener_fuente(best_size, bold)
    total_height = len(best_lines) * fuente.get_height()
    start_y = y + (h - total_height) // 2 if centrado else y

    for i, line in enumerate(best_lines):
        try:
            render = render_text_cached(line, best_size, bold, color)
        except Exception:
            render = render_text_cached(''.join([c if ord(c) < 100000 else ' ' for c in line]), best_size, bold, color)
        rect = render.get_rect()
        rect.centerx = x + w // 2 if centrado else x
        rect.y = start_y + i * fuente.get_height()
        pantalla.blit(render, rect)

def dibujar_caja_texto(
    pantalla, x, y, w, h, color, radius=18, texto=None, fuente=None, color_texto=(30, 30, 30)
):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, color, (0, 0, w, h), border_radius=radius)
    pantalla.blit(s, (x, y))
    if texto:
        mostrar_texto_adaptativo(
            pantalla, texto, x, y, w, h, fuente or get_default_font(), color_texto, centrado=True
        )

def dibujar_barra_scroll(
    surface, x, y, w, h, scroll_pos, total_height, visible_height, color=(200, 200, 200), highlight=False
):
    if total_height <= visible_height or h <= 0:
        return None

    bar_width = 10
    vis_ratio = visible_height / total_height
    thumb_height = max(30, int(visible_height * vis_ratio))
    max_scroll = total_height - visible_height
    if max_scroll == 0:
        thumb_pos = y
    else:
        thumb_pos = y + int(scroll_pos * (h - thumb_height) / max_scroll)

    bar_rect = pygame.Rect(x + w - bar_width, y, bar_width, h)
    pygame.draw.rect(surface, (100, 100, 100, 100), bar_rect, border_radius=5)

    thumb_color = (150, 180, 255) if highlight else color
    thumb_rect = pygame.Rect(x + w - bar_width, thumb_pos, bar_width, thumb_height)
    pygame.draw.rect(surface, thumb_color, thumb_rect, border_radius=5)

    return thumb_rect

# --- Inertial & Time-based Scroll Manager ---
class ScrollManager:
    def __init__(self, initial_pos=0):
        self.scroll_pos = initial_pos
        self.target_scroll = initial_pos
        self.last_update = time.time()
        self.dragging = False
        self.drag_offset = 0
        self.velocity = 0.0  # For inertial scrolling

    def update(self, max_scroll, smooth=True):
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time

        if smooth:
            diff = self.target_scroll - self.scroll_pos
            if abs(diff) > 0.5:
                self.velocity = diff * min(1.0, dt * 10)
                self.scroll_pos += self.velocity
            else:
                self.scroll_pos = self.target_scroll
                self.velocity = 0.0
        else:
            self.scroll_pos = self.target_scroll
            self.velocity = 0.0

        # Inertial effect
        if not self.dragging and abs(self.velocity) > 0.1:
            self.scroll_pos += self.velocity * dt * 10
            self.velocity *= 0.92  # Damping

        self.scroll_pos = max(0, min(self.scroll_pos, max_scroll))
        self.target_scroll = max(0, min(self.target_scroll, max_scroll))
        return int(self.scroll_pos)

    def scroll_to(self, pos):
        self.target_scroll = pos

    def scroll_by(self, delta):
        self.target_scroll += delta

    def handle_event(self, event, wheel_speed=40, thumb_rect=None, max_scroll=0, h=0, y=0, bar_rect=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_by(-wheel_speed)
                return True
            elif event.button == 5:
                self.scroll_by(wheel_speed)
                return True
            elif event.button == 1:
                if thumb_rect and thumb_rect.collidepoint(event.pos):
                    self.dragging = True
                    self.drag_offset = event.pos[1] - thumb_rect.y
                    return True
                elif bar_rect and bar_rect.collidepoint(event.pos):
                    click_y = event.pos[1]
                    bar_top = y
                    bar_height = h
                    thumb_height = thumb_rect.height if thumb_rect else 30
                    rel_y = click_y - bar_top - thumb_height // 2
                    max_thumb_y = bar_height - thumb_height
                    rel_y = max(0, min(rel_y, max_thumb_y))
                    if max_scroll > 0 and bar_height > thumb_height:
                        self.target_scroll = int(rel_y * max_scroll / (bar_height - thumb_height))
                    return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging and thumb_rect:
            new_thumb_y = event.pos[1] - self.drag_offset
            bar_height = h
            thumb_height = thumb_rect.height
            max_thumb_y = y + bar_height - thumb_height
            new_thumb_y = max(y, min(new_thumb_y, max_thumb_y))
            if max_scroll > 0 and bar_height > thumb_height:
                self.target_scroll = int((new_thumb_y - y) * max_scroll / (bar_height - thumb_height))
            return True
        return False

