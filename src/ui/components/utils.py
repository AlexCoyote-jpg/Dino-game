import pygame
import time
import unicodedata
from functools import lru_cache
from typing import Optional, Tuple, Dict, Any, List, Union, Callable

# --- Memory Management & Caching ---
FUENTE_NOMBRE = "Segoe UI Emoji"  # Cambiado a Segoe UI Emoji para mejor soporte de emojis

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

# --- Emoji Support ---
def is_emoji(char: str) -> bool:
    """Determina si un carácter es un emoji."""
    if not char:
        return False
    try:
        # Categorías comunes para emojis
        return unicodedata.category(char) in ('So', 'Sk', 'Sm', 'Sc')
    except:
        # Si hay error al procesar el carácter, asumimos que podría ser un emoji
        return True

def split_text_with_emojis(text: str) -> List[str]:
    """Divide el texto en segmentos, separando emojis para renderizado especial."""
    segments = []
    current_segment = ""
    
    for char in text:
        if is_emoji(char):
            # Si tenemos texto acumulado, lo guardamos primero
            if current_segment:
                segments.append(current_segment)
                current_segment = ""
            # Guardamos el emoji como un segmento separado
            segments.append(char)
        else:
            current_segment += char
    
    # Añadir el último segmento si existe
    if current_segment:
        segments.append(current_segment)
    
    return segments

# --- Tooltip Manager ---
class TooltipManager:
    def __init__(self, delay: float = 2.0, font_size: int = 16, 
                 bg_color: Tuple[int, int, int] = (50, 50, 50), 
                 text_color: Tuple[int, int, int] = (255, 255, 255),
                 padding: int = 8, border_radius: int = 6):
        self.delay = delay  # Segundos antes de mostrar el tooltip
        self.hover_start = None
        self.current_tooltip = None
        self.current_pos = (0, 0)
        self.font_size = font_size
        self.bg_color = bg_color
        self.text_color = text_color
        self.padding = padding
        self.border_radius = border_radius
        self.active_elements = {}  # {elemento_id: (texto, rect)}
    
    def register(self, element_id: str, tooltip_text: str, rect: pygame.Rect):
        """Registra un elemento para mostrar tooltip"""
        self.active_elements[element_id] = (tooltip_text, rect)
    
    def unregister(self, element_id: str):
        """Elimina un elemento registrado"""
        if element_id in self.active_elements:
            del self.active_elements[element_id]
    
    def update(self, mouse_pos: Tuple[int, int]):
        """Actualiza el estado del tooltip basado en la posición del mouse"""
        current_time = time.time()
        
        # Verificar si el mouse está sobre algún elemento registrado
        for element_id, (tooltip_text, rect) in self.active_elements.items():
            if rect.collidepoint(mouse_pos):
                if self.hover_start is None:
                    # Comenzar a contar el tiempo de hover
                    self.hover_start = current_time
                    self.current_tooltip = tooltip_text
                    # Posicionar el tooltip encima del elemento
                    self.current_pos = (rect.centerx, rect.y - 10)
                elif current_time - self.hover_start >= self.delay:
                    # Ya pasó el tiempo de delay, mantener el tooltip activo
                    return True
                return False
        
        # Si el mouse no está sobre ningún elemento, resetear
        self.hover_start = None
        self.current_tooltip = None
        return False
    
    def draw(self, pantalla):
        """Dibuja el tooltip si está activo"""
        if self.hover_start is None or self.current_tooltip is None:
            return
        
        current_time = time.time()
        if current_time - self.hover_start < self.delay:
            return
        
        # Crear superficie para el fondo
        font = obtener_fuente(self.font_size, False)
        # Estimar el ancho del texto
        text_width = font.size(self.current_tooltip)[0]
        width = text_width + self.padding * 2
        height = font.get_height() + self.padding * 2
        
        # Posicionar el tooltip para que no se salga de la pantalla
        x = max(0, min(self.current_pos[0] - width // 2, pantalla.get_width() - width))
        y = max(0, self.current_pos[1] - height)
        
        # Dibujar fondo con transparencia
        tooltip_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(tooltip_surf, (*self.bg_color, 220), 
                         (0, 0, width, height), 
                         border_radius=self.border_radius)
        pantalla.blit(tooltip_surf, (x, y))
        
        # Renderizar el texto del tooltip
        mostrar_texto_adaptativo(
            pantalla=pantalla,
            texto=self.current_tooltip,
            x=x + self.padding,
            y=y + self.padding,
            w=width - self.padding * 2,
            h=height - self.padding * 2,
            fuente_base=font,
            color=self.text_color,
            centrado=True
        )
        
        # Marcar el área como dirty para actualización parcial
        mark_dirty(pygame.Rect(x, y, width, height))

# --- Unified Button Class with Click Support ---
class Boton:
    """
    Botón unificado con soporte para imágenes, tooltips, personalización de posición de imagen, 
    texto, colores, bordes, radios, estilos, optimización de renderizado y detección de clicks.
    """
    def __init__(
        self,
        texto: str,
        x: int,
        y: int,
        ancho: int,
        alto: int,
        id: Optional[str] = None,
        tooltip: Optional[str] = None,
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
        texto_adaptativo: bool = True,  # Por defecto adaptativo
        on_click: Optional[Callable[[], None]] = None,
    ):
        self.texto = texto
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.id = id or f"btn_{x}_{y}_{texto}"
        self.tooltip = tooltip
        self.imagen = imagen
        self.imagen_pos = imagen_pos
        self.imagen_padding = imagen_padding
        self.imagen_alpha = imagen_alpha
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.color_texto = color_texto
        
        # Configuración de fuente
        if fuente:
            self.fuente = fuente
        elif fuente_size:
            self.fuente = obtener_fuente(fuente_size, texto_negrita)
        else:
            self.fuente = get_default_font()
            
        if texto_negrita:
            self.fuente.set_bold(texto_negrita)
        if texto_cursiva:
            self.fuente.set_italic(texto_cursiva)
        if texto_subrayado:
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
        self.texto_adaptativo = texto_adaptativo
        self._shadow_surf = self._make_shadow()
        self._gradiente_cache = None
        self._last_hovered = None
        
        # Estado para tooltips y clicks
        self.hovered = False
        self.clicked = False
        self.on_click = on_click
        self.last_click_time = 0
        self.click_cooldown = 0.2  # Tiempo mínimo entre clicks (segundos)

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

    def draw(self, pantalla, tooltip_manager: Optional[TooltipManager] = None):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.collidepoint(mouse_pos)
        
        # Registrar para tooltips si es necesario
        if tooltip_manager and self.tooltip:
            tooltip_manager.register(self.id, self.tooltip, self.rect)
        
        if self.estilo == "apple":
            self._draw_apple(pantalla, self.hovered)
        elif self.estilo == "round":
            self._draw_round(pantalla, self.hovered)
        else:
            self._draw_flat(pantalla, self.hovered)
        
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

        # Layout imagen (ajuste de tamaño para que no sobresalga)
        if img:
            max_img_w = area.width // 2 if self.imagen_pos in ("left", "right") else area.width
            max_img_h = area.height // 2 if self.imagen_pos in ("top", "bottom") else area.height
            scale = min(max_img_w / img_rect.width, max_img_h / img_rect.height, 1.0)
            new_w = int(img_rect.width * scale)
            new_h = int(img_rect.height * scale)
            # Prevent negative or zero sizes for scaling
            if new_w > 0 and new_h > 0:
                img = pygame.transform.smoothscale(img, (new_w, new_h))
                img_rect = img.get_rect()
            else:
                # Skip scaling and drawing if size is invalid
                img = None
                img_rect = pygame.Rect(0, 0, 0, 0)
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

        # Layout texto adaptativo
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
            if img and self.imagen_pos in ("top", "bottom"):
                img_h = img_rect.height + self.imagen_padding
                if self.imagen_pos == "top":
                    text_area_y += img_h
                    text_area_h -= img_h
                else:
                    text_area_h -= img_h

            if self.texto_adaptativo:
                mostrar_texto_adaptativo(
                    pantalla=pantalla, 
                    texto=self.texto,
                    x=text_area_x, 
                    y=text_area_y, 
                    w=text_area_w, 
                    h=text_area_h,
                    fuente_base=self.fuente, 
                    color=self.color_texto,
                    centrado=(self.texto_alineacion == "center")
                )
            else:
                lines = self.texto.split('\n')
                text_surfs = []
                
                for line in lines:
                    segments = split_text_with_emojis(line)
                    line_surfs = []
                    
                    for segment in segments:
                        try:
                            surf = self.fuente.render(segment, True, self.color_texto)
                            line_surfs.append(surf)
                        except:
                            # Si falla al renderizar (posiblemente un emoji no soportado)
                            fallback = '□'  # Carácter de reemplazo
                            surf = self.fuente.render(fallback, True, self.color_texto)
                            line_surfs.append(surf)
                    
                    # Combinar los segmentos en una sola superficie para esta línea
                    if line_surfs:
                        total_width = sum(s.get_width() for s in line_surfs)
                        max_height = max(s.get_height() for s in line_surfs)
                        line_surface = pygame.Surface((total_width, max_height), pygame.SRCALPHA)
                        
                        x_offset = 0
                        for surf in line_surfs:
                            line_surface.blit(surf, (x_offset, 0))
                            x_offset += surf.get_width()
                        
                        text_surfs.append(line_surface)
                
                if text_surfs:
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
    
    def handle_event(self, event):
        """
        Maneja eventos para el botón, especialmente clicks.
        Retorna True si el botón fue clickeado y procesó el evento.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Click izquierdo
            if self.collidepoint(event.pos):
                current_time = time.time()
                # Verificar cooldown para evitar doble clicks accidentales
                if current_time - self.last_click_time > self.click_cooldown:
                    self.last_click_time = current_time
                    self.clicked = True
                    if self.on_click:
                        self.on_click()
                    return True
        return False
    
    def check_click(self):
        """
        Verifica si el botón ha sido clickeado y resetea el estado.
        Útil para polling en lugar de event handling.
        """
        was_clicked = self.clicked
        self.clicked = False
        return was_clicked

# --- Adaptive Text Rendering with Emoji Support ---
def mostrar_texto_adaptativo(
    pantalla: pygame.Surface,
    texto: str,
    x: int,
    y: int,
    w: int,
    h: int,
    fuente_base: Optional[pygame.font.Font] = None,
    color: Tuple[int, int, int] = (30, 30, 30),
    centrado: bool = False,
    es_tooltip: bool = False,
    bg_color: Optional[Tuple[int, int, int, int]] = None,
    border_radius: int = 6,
    padding: int = 8
):
    """
    Muestra texto adaptativo con soporte para emojis y saltos de línea.
    Ajusta el tamaño de fuente para que el texto no sobresalga ni en ancho ni en alto.
    """
    fuente_base = fuente_base or get_default_font()
    max_font_size = fuente_base.get_height()
    min_font_size = 10
    bold = fuente_base.get_bold()

    # Divide el texto en líneas por \n
    lines = texto.split('\n')
    best_size = min_font_size
    best_surfs = []
    # Búsqueda binaria para el tamaño de fuente máximo que cabe en el área
    left, right = min_font_size, max_font_size
    while left <= right:
        mid = (left + right) // 2
        fuente = obtener_fuente(mid, bold)
        line_surfs = []
        max_line_w = 0
        for line in lines:
            # Renderiza cada línea, soportando emojis
            segments = split_text_with_emojis(line)
            seg_surfs = []
            for seg in segments:
                try:
                    seg_surfs.append(fuente.render(seg, True, color))
                except:
                    seg_surfs.append(fuente.render('□', True, color))
            if seg_surfs:
                total_w = sum(s.get_width() for s in seg_surfs)
                max_h = max(s.get_height() for s in seg_surfs)
                line_surf = pygame.Surface((total_w, max_h), pygame.SRCALPHA)
                x_off = 0
                for s in seg_surfs:
                    line_surf.blit(s, (x_off, 0))
                    x_off += s.get_width()
                line_surfs.append(line_surf)
                max_line_w = max(max_line_w, total_w)
            else:
                line_surfs.append(None)
        total_height = sum((s.get_height() if s else 0) for s in line_surfs)
        if max_line_w <= w and total_height <= h:
            best_size = mid
            best_surfs = line_surfs
            left = mid + 1
        else:
            right = mid - 1

    # Render final con el mejor tamaño encontrado
    fuente = obtener_fuente(best_size, bold)
    y_offset = y + (h - sum((s.get_height() if s else 0) for s in best_surfs)) // 2 if centrado else y
    for s in best_surfs:
        if s:
            if centrado:
                x_offset = x + (w - s.get_width()) // 2
            else:
                x_offset = x
            pantalla.blit(s, (x_offset, y_offset))
            y_offset += s.get_height()

def dibujar_caja_texto(
    pantalla, x, y, w, h, color, radius=18, texto=None, fuente=None, color_texto=(30, 30, 30)
):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, color, (0, 0, w, h), border_radius=radius)
    pantalla.blit(s, (x, y))
    if texto:
        mostrar_texto_adaptativo(
            pantalla=pantalla, 
            texto=texto, 
            x=x, 
            y=y, 
            w=w, 
            h=h, 
            fuente_base=fuente or get_default_font(), 
            color=color_texto, 
            centrado=True
        )

def dibujar_barra_scroll(
    surface, x, y, w, h, scroll_pos, total_height, visible_height, color=(200, 200, 200), highlight=False
):
    # Thumb más visible y soporte visual para arrastre
    if total_height <= visible_height or h <= 0:
        return None

    bar_width = 16  # Más ancho para mejor usabilidad
    vis_ratio = visible_height / total_height
    thumb_height = max(30, int(visible_height * vis_ratio))
    max_scroll = total_height - visible_height
    if max_scroll == 0:
        thumb_pos = y
    else:
        thumb_pos = y + int(scroll_pos * (h - thumb_height) / max_scroll)

    bar_rect = pygame.Rect(x + w - bar_width, y, bar_width, h)
    pygame.draw.rect(surface, (100, 100, 100, 120), bar_rect, border_radius=8)

    thumb_color = (120, 180, 255) if highlight else color
    thumb_rect = pygame.Rect(x + w - bar_width, thumb_pos, bar_width, thumb_height)
    pygame.draw.rect(surface, thumb_color, thumb_rect, border_radius=8)
    # Línea central para mejor feedback visual
    pygame.draw.line(surface, (80, 120, 180), (thumb_rect.centerx, thumb_rect.y+8), (thumb_rect.centerx, thumb_rect.bottom-8), 4)

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

# --- Ejemplo de uso ---
def ejemplo_uso():
    """Demostración de scroll, botones (con y sin imagen), tooltips, emojis y cajas de texto."""
    pygame.init()
    pantalla = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Demo UI: Botones, Tooltips, Scroll, Emojis, Cajas de Texto")
    reloj = pygame.time.Clock()

    # Cargar imagen para botones (si existe)
    try:
        dino_img = pygame.image.load("assets/imagenes/dino1.png").convert_alpha()
    except Exception:
        dino_img = None

    tooltip_manager = TooltipManager(delay=1.0)

    # Botones de todos los estilos y variantes
    botones = [
        Boton(
            texto="Apple 🚀", x=40, y=40, ancho=180, alto=50,
            tooltip="Botón estilo Apple", estilo="apple",
            color_normal=(220, 230, 245), color_hover=(180, 210, 255),
            on_click=lambda: print("Apple!"),
        ),
        Boton(
            texto="Flat 🔥", x=240, y=40, ancho=180, alto=50,
            tooltip="Botón estilo Flat", estilo="flat",
            color_normal=(200, 220, 255), color_hover=(180, 200, 255),
            on_click=lambda: print("Flat!"),
        ),
        Boton(
            texto="Round 👍", x=440, y=30, ancho=70, alto=70,
            tooltip="Botón estilo Round", estilo="round",
            color_normal=(255, 200, 200), color_hover=(255, 180, 180),
            on_click=lambda: print("Round!"),
        ),
        Boton(
            texto="Con Imagen", x=540, y=40, ancho=180, alto=50,
            tooltip="Botón con imagen", estilo="apple",
            imagen=dino_img, imagen_pos="left",
            color_normal=(220, 245, 220), color_hover=(180, 255, 180),
            on_click=lambda: print("Con Imagen!"),
        ),
        Boton(
            texto="Emoji 🦖", x=740, y=40, ancho=120, alto=50,
            tooltip="Botón con emoji y tooltip largo para probar el adaptativo 🦖",
            estilo="flat", color_normal=(255, 255, 200),
            on_click=lambda: print("Emoji!"),
        ),
    ]

    # Cajas de texto de diferentes tamaños, calculadas dinámicamente según pantalla
    caja_texto = "Caja de texto adaptativa con emojis: 🦖🎮🚀🔥"
    ancho_pantalla, alto_pantalla = pantalla.get_size()
    cajas = []
    n_cajas = 4
    for i in range(n_cajas):
        w = int(ancho_pantalla * (0.18 + 0.08 * i))
        h = int(alto_pantalla * (0.08 + 0.04 * i))
        x = int(ancho_pantalla * 0.35)
        y = int(alto_pantalla * (0.15 + 0.13 * i))
        cajas.append((x, y, w, h))

    # Área de scroll dinámica
    scroll_area_w = int(ancho_pantalla * 0.28)
    scroll_area_h = int(alto_pantalla * 0.38)
    scroll_area_x = int(ancho_pantalla * 0.03)
    scroll_area_y = int(alto_pantalla * 0.18)
    scroll_area = pygame.Rect(scroll_area_x, scroll_area_y, scroll_area_w, scroll_area_h)
    scroll_lineas = max(20, int(scroll_area_h / 18) + 10)
    scroll_text = "Scroll demo\n" + "\n".join([f"Línea {i+1} 😊" for i in range(scroll_lineas)])
    scroll_manager = ScrollManager()
    # Calcula la altura del contenido de scroll dinámicamente
    temp_surf = pygame.Surface((scroll_area_w - 20, 10000), pygame.SRCALPHA)
    mostrar_texto_adaptativo(
        pantalla=temp_surf,
        texto=scroll_text,
        x=0, y=0, w=scroll_area_w - 20, h=10000,
        fuente_base=obtener_fuente(20, False),
        color=(50, 50, 50),
        centrado=False
    )
    # Encuentra la última línea pintada para ajustar el alto real
    non_empty = [y for y in range(temp_surf.get_height()) if temp_surf.get_at((1, y))[3] > 0]
    if non_empty:
        scroll_content_height = non_empty[-1] + 30
    else:
        scroll_content_height = scroll_area_h

    ejecutando = True
    thumb_rect = None
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            for boton in botones:
                boton.handle_event(evento)
            scroll_manager.handle_event(
                evento,
                wheel_speed=40,
                thumb_rect=thumb_rect,
                max_scroll=scroll_content_height - scroll_area.height,
                h=scroll_area.height,
                y=scroll_area.y,
                bar_rect=pygame.Rect(scroll_area.right - 16, scroll_area.y, 16, scroll_area.height)
            )

        pantalla.fill((240, 240, 240))

        tooltip_manager.update(pygame.mouse.get_pos())

        for boton in botones:
            boton.draw(pantalla, tooltip_manager)

        for x, y, w, h in cajas:
            dibujar_caja_texto(
                pantalla, x, y, w, h,
                color=(200, 220, 255, 220),
                radius=12,
                texto=caja_texto,
                fuente=obtener_fuente(18, False),
                color_texto=(30, 30, 60)
            )

        # Área de scroll: solo pinta donde hay contenido, el resto fondo
        pygame.draw.rect(pantalla, (220, 220, 220), scroll_area, border_radius=10)
        scroll_y = scroll_manager.update(scroll_content_height - scroll_area.height)
        scroll_surface = pygame.Surface((scroll_area.width, scroll_content_height), pygame.SRCALPHA)
        mostrar_texto_adaptativo(
            pantalla=scroll_surface,
            texto=scroll_text,
            x=10, y=10, w=scroll_area.width - 20, h=scroll_content_height - 20,
            fuente_base=obtener_fuente(20, False),
            color=(50, 50, 50),
            centrado=False
        )
        visible_h = min(scroll_area.height, scroll_content_height - scroll_y)
        if visible_h > 0:
            visible_rect = pygame.Rect(0, scroll_y, scroll_area.width - 16, visible_h)
            pantalla.blit(scroll_surface, (scroll_area.x, scroll_area.y), area=visible_rect)
        if scroll_content_height - scroll_y < scroll_area.height:
            empty_y = scroll_area.y + (scroll_content_height - scroll_y)
            empty_h = scroll_area.height - (scroll_content_height - scroll_y)
            if empty_h > 0:
                pygame.draw.rect(
                    pantalla, (220, 220, 220),
                    (scroll_area.x, empty_y, scroll_area.width - 16, empty_h)
                )
        thumb_rect = dibujar_barra_scroll(
            pantalla, scroll_area.x, scroll_area.y, scroll_area.width, scroll_area.height,
            scroll_y, scroll_content_height, scroll_area.height, color=(150, 180, 255), highlight=True
        )

        tooltip_manager.draw(pantalla)

        mostrar_texto_adaptativo(
            pantalla=pantalla,
            texto="Texto adaptativo con emojis: 😊 🎮 🐍 ⭐ 🔥\n¡Prueba todos los controles!\n hola",
            x=int(ancho_pantalla * 0.04), y=int(alto_pantalla * 0.7), w=int(ancho_pantalla * 0.64), h=int(alto_pantalla * 0.12),
            fuente_base=obtener_fuente(24, False),
            color=(50, 50, 50),
            centrado=True
        )

        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()

if __name__ == "__main__":
    ejemplo_uso()