import pygame
import time
import threading

def dibujar_barra_scroll(superficie, x, y, ancho, alto, scroll_pos, contenido_alto, ventana_alto, 
                         color=(120, 180, 255), highlight=False, modern=True):
    if contenido_alto <= ventana_alto:
        return

    # Definir colores y parámetros solo una vez
    pastel_bg = (245, 230, 255, 120)
    thumb_color = (180, 220, 255) if highlight else (140, 200, 255)
    thumb_border = (90, 170, 240)
    thumb_gloss = (255, 255, 255, 90)
    thumb_radius = max(ancho // 2, 8)
    thumb_min_height = max(40, ventana_alto // 8)

    # Calcular tamaño y posición del thumb
    barra_alto = max(thumb_min_height, ventana_alto * ventana_alto / contenido_alto)
    barra_pos = y + (scroll_pos * (alto - barra_alto) / (contenido_alto - ventana_alto))

    # Fondo de barra (solo una superficie, sin alpha si no es necesario)
    s_bg = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    pygame.draw.rect(s_bg, pastel_bg, s_bg.get_rect(), border_radius=ancho)
    superficie.blit(s_bg, (x, y))

    # Thumb principal (reutilizar superficies si es posible en el ciclo principal)
    s_thumb = pygame.Surface((ancho, int(barra_alto)), pygame.SRCALPHA)
    pygame.draw.rect(s_thumb, thumb_color, s_thumb.get_rect(), border_radius=thumb_radius)
    grad = pygame.Surface((ancho, int(barra_alto)//2), pygame.SRCALPHA)
    pygame.draw.rect(grad, thumb_gloss, grad.get_rect(), border_radius=thumb_radius)
    s_thumb.blit(grad, (0, 0))
    superficie.blit(s_thumb, (x, barra_pos))

    # Borde del thumb
    pygame.draw.rect(superficie, thumb_border, pygame.Rect(x, barra_pos, ancho, barra_alto), 3, border_radius=thumb_radius)

    # Carita decorativa solo si es suficientemente grande
    if barra_alto >= 48 and ancho >= 24:
        cx, cy = x + ancho // 2, int(barra_pos + barra_alto // 2)
        pygame.draw.circle(superficie, (255, 255, 255), (cx-6, cy-7), 2)
        pygame.draw.circle(superficie, (255, 255, 255), (cx+6, cy-7), 2)
        pygame.draw.arc(superficie, (255, 255, 255), (cx-7, cy-2, 14, 10), 3.7, 5.7, 2)

class ScrollManager:
    def __init__(self):
        # Variable de posición actual y destino para el scroll
        self.scroll_pos = 0
        self.target_scroll = 0
        # Lock para asegurar acceso thread-safe
        self._lock = threading.Lock()
        self.last_update = time.time()
        self.dragging = False
        self.drag_offset = 0
        self.velocity = 0.0

    def update(self, max_scroll, smooth=True):
        """
        Actualiza gradualmente la posición actual del scroll hacia el objetivo.
        
        Args:
            max_scroll (int): Valor máximo de scroll.
            smooth (bool): Si se utiliza interpolación suave.
            
        Returns:
            int: La posición de scroll actualizada.
        """
        with self._lock:
            now = time.time()
            dt = now - self.last_update
            self.last_update = now

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

            if not self.dragging and abs(self.velocity) > 0.1:
                self.scroll_pos += self.velocity * dt * 10
                self.velocity *= 0.92

            # Clamp scroll positions
            self.scroll_pos = max(0, min(self.scroll_pos, max_scroll))
            self.target_scroll = max(0, min(self.target_scroll, max_scroll))
            return int(self.scroll_pos)

    def scroll_to(self, pos):
        self.target_scroll = pos

    def scroll_by(self, delta):
        self.target_scroll += delta

    def scroll_to_bottom(self, target_offset, instant=False):
        """
        Establece el target de scroll, con opción de aplicarlo inmediatamente.
        
        Args:
            target_offset: El offset objetivo para el scroll
            instant: Si es True, aplica el scroll instantáneamente
        """
        with self._lock:
            self.target_scroll = target_offset
            if instant:
                self.scroll_pos = target_offset

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
                    thumb_height = thumb_rect.height if thumb_rect else 30
                    rel_y = click_y - y - thumb_height // 2
                    max_thumb_y = h - thumb_height
                    rel_y = max(0, min(rel_y, max_thumb_y))
                    if max_scroll > 0 and h > thumb_height:
                        self.target_scroll = int(rel_y * max_scroll / (h - thumb_height))
                    return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging and thumb_rect:
            new_thumb_y = event.pos[1] - self.drag_offset
            thumb_height = thumb_rect.height
            max_thumb_y = y + h - thumb_height
            new_thumb_y = max(y, min(new_thumb_y, max_thumb_y))
            if max_scroll > 0 and h > thumb_height:
                self.target_scroll = int((new_thumb_y - y) * max_scroll / (h - thumb_height))
            return True
        return False
