import pygame
import tkinter as tk
import math
from ui.components.utils import Boton
from contextlib import suppress

class ChatInputManager:
    def __init__(self, scaler, input_rect, font, on_send_callback, chatbot=None):
        self.texto_usuario = ""
        self.font = font
        self.scaler = scaler
        self.input_rect = input_rect
        self.cursor_visible = True
        self.last_cursor_toggle = 0
        self.cursor_interval = 500  # ms
        self.last_backspace_time = 0
        self.backspace_delay = 50  # ms
        self.backspace_repeat_delay = 300  # ms
        self.backspace_held = False
        self.backspace_first_press_time = 0
        self.esperando_respuesta = False
        self._voz_reproduciendo = False
        self._chatbot = chatbot
        self.cursor_pos = 0
        self.selection_start = 0
        self.selection_end = 0
        self._undo_stack = []
        self._undo_limit = 50
        self._mouse_selecting = False
        # Iconos y botones
        self._init_buttons(on_send_callback)
        # Barra de carga
        self._loading_border_thickness = 4
        self._loading_border_colors = ((255, 120, 120), (255, 170, 200))
        self._update_loading_border_points()

    def _init_buttons(self, on_send_callback):
        btn_size = min(self.input_rect.height - 2, self.scaler.scale_x_value(48))
        self.btn_size = btn_size
        # Botón enviar
        icon_img = self._load_icon("assets/imagenes/enviar.png", btn_size)
        self.boton_enviar = Boton(
            texto="",
            x=self.input_rect.right - btn_size,
            y=self.input_rect.y + (self.input_rect.height - btn_size) // 2,
            ancho=btn_size,
            alto=btn_size,
            imagen=icon_img,
            imagen_pos="center",
            color_top=(255, 120, 120),
            color_bottom=(255, 170, 200),
            color_hover=(255, 140, 160),
            border_radius=btn_size // 2,
            estilo="round",
            on_click=on_send_callback
        )
        # Botón voz
        voz_img = self._load_icon("assets/imagenes/voz.png", btn_size)
        voz_btn_x = self.input_rect.x + 8
        voz_btn_y = self.input_rect.y + (self.input_rect.height - btn_size) // 2
        self.boton_voz = Boton(
            texto="",
            x=voz_btn_x,
            y=voz_btn_y,
            ancho=btn_size,
            alto=btn_size,
            imagen=voz_img,
            imagen_pos="center",
            color_top=(120, 200, 255),
            color_bottom=(180, 240, 255),
            color_hover=(100, 180, 220),
            border_radius=btn_size // 2,
            estilo="round",
            on_click=self._on_voice_click
        )

    def _load_icon(self, path, size):
        try:
            img = pygame.image.load(path).convert_alpha()
            if img.get_width() != size or img.get_height() != size:
                img = pygame.transform.smoothscale(img, (size, size))
            return img
        except Exception:
            return None

    def _update_loading_border_points(self):
        rect = self.input_rect.inflate(self._loading_border_thickness*2, self._loading_border_thickness*2)
        w, h = rect.width, rect.height
        border_radius = self.input_rect.height // 2
        r = border_radius + 2
        self._loading_border_r = r
        w_line = max(1, w - 2*r)
        h_line = max(1, h - 2*r)
        points = []
        for i in range(w_line): points.append((rect.left + r + i, rect.top))
        for i in range(0, 91, 2):
            angle = (i / 180) * math.pi
            points.append((rect.right - r + r * math.cos(angle), rect.top + r - r * math.sin(angle)))
        for i in range(h_line): points.append((rect.right, rect.top + r + i))
        for i in range(0, 91, 2):
            angle = (i / 180) * math.pi
            points.append((rect.right - r + r * math.cos(angle), rect.bottom - r + r * math.sin(angle)))
        for i in range(w_line): points.append((rect.right - r - i, rect.bottom))
        for i in range(0, 91, 2):
            angle = (i / 180) * math.pi
            points.append((rect.left + r - r * math.cos(angle), rect.bottom - r + r * math.sin(angle)))
        for i in range(h_line): points.append((rect.left, rect.bottom - r - i))
        for i in range(0, 91, 2):
            angle = (i / 180) * math.pi
            points.append((rect.left + r - r * math.cos(angle), rect.top + r - r * math.sin(angle)))
        self._loading_border_points = points
        self._loading_border_perimeter = len(points)
        self._loading_border_chunk_len = int(self._loading_border_perimeter * 0.18)
        self._loading_border_last_rect = rect

    def _has_selection(self):
        return self.selection_start != self.selection_end

    def _get_selection_range(self):
        return min(self.selection_start, self.selection_end), max(self.selection_start, self.selection_end)

    def _delete_selection(self):
        if self._has_selection():
            start, end = self._get_selection_range()
            self.texto_usuario = self.texto_usuario[:start] + self.texto_usuario[end:]
            self.cursor_pos = start
            self.selection_start = self.selection_end = self.cursor_pos

    def _push_undo(self):
        if len(self._undo_stack) >= self._undo_limit:
            self._undo_stack.pop(0)
        self._undo_stack.append((self.texto_usuario, self.cursor_pos, self.selection_start, self.selection_end))

    def _pop_undo(self):
        if self._undo_stack:
            last = self._undo_stack.pop()
            self.texto_usuario, self.cursor_pos, self.selection_start, self.selection_end = last

    def _get_char_index_from_mouse(self, mx, text_x, scroll_offset):
        x = mx - text_x + scroll_offset
        if not self.texto_usuario:
            return 0
        left, right = 0, len(self.texto_usuario)
        while left < right:
            mid = (left + right) // 2
            w = self.font.size(self.texto_usuario[:mid+1])[0]
            if x < w:
                right = mid
            else:
                left = mid + 1
        return left

    def _on_voice_click(self):
        if not self._hay_mensaje_ia():
            return
        if self._voz_reproduciendo:
            if self._chatbot:
                self._chatbot.detener_audio()
            self._voz_reproduciendo = False
        else:
            if self._chatbot:
                self._chatbot.hablar_ultimo_mensaje_bot()
            self._voz_reproduciendo = True

    def _hay_mensaje_ia(self):
        if not self._chatbot or not hasattr(self._chatbot, 'historial'):
            return False
        for autor, texto in reversed(self._chatbot.historial):
            if autor == "bot" and texto.strip():
                return True
        return False

    def _calcular_scroll_offset(self, rendered_pre, rendered_full, max_width):
        """Calcula el scroll horizontal necesario para que el cursor y el texto sean visibles."""
        if rendered_full.get_width() > max_width:
            if rendered_pre.get_width() > max_width:
                return rendered_pre.get_width() - max_width + 10
            elif rendered_full.get_width() - rendered_pre.get_width() < max_width:
                return rendered_full.get_width() - max_width
        return 0

    def handle_event(self, event, esperando_respuesta):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            self.boton_enviar.handle_event(event)
            self.boton_voz.handle_event(event)
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            shift = mods & pygame.KMOD_SHIFT
            ctrl = mods & pygame.KMOD_CTRL
            if event.key == pygame.K_z and ctrl:
                self._pop_undo()
                return None
            if (event.key in (pygame.K_BACKSPACE, pygame.K_DELETE) or
                (event.unicode and event.unicode.isprintable()) or
                (event.key == pygame.K_v and ctrl) or
                (event.key == pygame.K_x and ctrl)):
                self._push_undo()
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return 'send'
            elif event.key == pygame.K_c and ctrl:
                if self._has_selection():
                    start, end = self._get_selection_range()
                    with suppress(Exception):
                        r = tk.Tk(); r.withdraw(); r.clipboard_clear(); r.clipboard_append(self.texto_usuario[start:end]); r.update(); r.destroy()
            elif event.key == pygame.K_x and ctrl:
                if self._has_selection():
                    start, end = self._get_selection_range()
                    with suppress(Exception):
                        r = tk.Tk(); r.withdraw(); r.clipboard_clear(); r.clipboard_append(self.texto_usuario[start:end]); r.update(); r.destroy()
                    self._delete_selection()
            elif event.key == pygame.K_v and ctrl:
                with suppress(Exception):
                    r = tk.Tk(); r.withdraw(); clip = r.clipboard_get(); self._delete_selection(); self.texto_usuario = self.texto_usuario[:self.cursor_pos] + clip + self.texto_usuario[self.cursor_pos:]; self.cursor_pos += len(clip); self.selection_start = self.selection_end = self.cursor_pos; r.destroy()
            elif event.key == pygame.K_BACKSPACE:
                if self._has_selection():
                    self._delete_selection()
                elif self.cursor_pos > 0:
                    self.texto_usuario = self.texto_usuario[:self.cursor_pos-1] + self.texto_usuario[self.cursor_pos:]
                    self.cursor_pos -= 1
                self.last_backspace_time = pygame.time.get_ticks()
                self.backspace_first_press_time = self.last_backspace_time
                self.backspace_held = True
                self.selection_start = self.selection_end = self.cursor_pos
            elif event.key == pygame.K_DELETE:
                if self._has_selection():
                    self._delete_selection()
                elif self.cursor_pos < len(self.texto_usuario):
                    self.texto_usuario = self.texto_usuario[:self.cursor_pos] + self.texto_usuario[self.cursor_pos+1:]
                self.selection_start = self.selection_end = self.cursor_pos
            elif event.key == pygame.K_LEFT:
                if ctrl:
                    if self.cursor_pos > 0:
                        pos = self.cursor_pos - 1
                        while pos > 0 and self.texto_usuario[pos].isspace(): pos -= 1
                        while pos > 0 and not self.texto_usuario[pos-1].isspace(): pos -= 1
                        self.cursor_pos = pos
                else:
                    if self.cursor_pos > 0: self.cursor_pos -= 1
                if shift: self.selection_end = self.cursor_pos
                else: self.selection_start = self.selection_end = self.cursor_pos
            elif event.key == pygame.K_RIGHT:
                if ctrl:
                    pos = self.cursor_pos
                    n = len(self.texto_usuario)
                    while pos < n and not self.texto_usuario[pos].isspace(): pos += 1
                    while pos < n and self.texto_usuario[pos].isspace(): pos += 1
                    self.cursor_pos = pos
                else:
                    if self.cursor_pos < len(self.texto_usuario): self.cursor_pos += 1
                if shift: self.selection_end = self.cursor_pos
                else: self.selection_start = self.selection_end = self.cursor_pos
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
                if shift: self.selection_end = self.cursor_pos
                else: self.selection_start = self.selection_end = self.cursor_pos
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.texto_usuario)
                if shift: self.selection_end = self.cursor_pos
                else: self.selection_start = self.selection_end = self.cursor_pos
            elif event.unicode and event.unicode.isprintable():
                self._delete_selection()
                self.texto_usuario = self.texto_usuario[:self.cursor_pos] + event.unicode + self.texto_usuario[self.cursor_pos:]
                self.cursor_pos += 1
                self.selection_start = self.selection_end = self.cursor_pos
            self.cursor_pos = max(0, min(self.cursor_pos, len(self.texto_usuario)))
            self.selection_start = max(0, min(self.selection_start, len(self.texto_usuario)))
            self.selection_end = max(0, min(self.selection_end, len(self.texto_usuario)))
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                self.backspace_held = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not esperando_respuesta:
            mx, my = event.pos
            text_area_right = self.boton_enviar.x - 16
            text_area_left = self.boton_voz.x + self.boton_voz.ancho + 8
            text_x = text_area_left
            max_text_width = text_area_right - text_x
            rendered_full = self.font.render(self.texto_usuario, True, (120, 120, 120) if self.texto_usuario else (180, 180, 185))
            rendered_pre = self.font.render(self.texto_usuario[:self.cursor_pos], True, (120, 120, 120) if self.texto_usuario else (180, 180, 185))
            scroll_offset = self._calcular_scroll_offset(rendered_pre, rendered_full, max_text_width)
            if self.input_rect.collidepoint(mx, my):
                idx = self._get_char_index_from_mouse(mx, text_x, scroll_offset)
                self.cursor_pos = idx
                self.selection_start = self.selection_end = idx
                self._mouse_selecting = True
        elif event.type == pygame.MOUSEMOTION and self._mouse_selecting and not esperando_respuesta:
            mx, my = event.pos
            text_area_right = self.boton_enviar.x - 16
            text_area_left = self.boton_voz.x + self.boton_voz.ancho + 8
            text_x = text_area_left
            max_text_width = text_area_right - text_x
            rendered_full = self.font.render(self.texto_usuario, True, (120, 120, 120) if self.texto_usuario else (180, 180, 185))
            rendered_pre = self.font.render(self.texto_usuario[:self.cursor_pos], True, (120, 120, 120) if self.texto_usuario else (180, 180, 185))
            scroll_offset = self._calcular_scroll_offset(rendered_pre, rendered_full, max_text_width)
            if self.input_rect.collidepoint(mx, my):
                idx = self._get_char_index_from_mouse(mx, text_x, scroll_offset)
                self.cursor_pos = idx
                self.selection_end = idx
        elif event.type == pygame.MOUSEBUTTONUP:
            self._mouse_selecting = False
        return None

    def update(self):
        if self.backspace_held:
            current_time = pygame.time.get_ticks()
            if current_time - self.backspace_first_press_time > self.backspace_repeat_delay:
                if current_time - self.last_backspace_time >= self.backspace_delay:
                    if self._has_selection():
                        self._delete_selection()
                    elif self.cursor_pos > 0:
                        self.texto_usuario = self.texto_usuario[:self.cursor_pos-1] + self.texto_usuario[self.cursor_pos:]
                        self.cursor_pos -= 1
                    self.last_backspace_time = current_time
            self.cursor_pos = max(0, min(self.cursor_pos, len(self.texto_usuario)))
            self.selection_start = max(0, min(self.selection_start, len(self.texto_usuario)))
            self.selection_end = max(0, min(self.selection_end, len(self.texto_usuario)))
        now = pygame.time.get_ticks()
        if now - self.last_cursor_toggle > self.cursor_interval:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = now

    def draw(self, pantalla, esperando_respuesta):
        input_bg_color = (255, 255, 255)
        shadow_color = (230, 230, 230)
        border_radius = self.input_rect.height // 2
        shadow_rect = self.input_rect.move(0, 6)
        pygame.draw.rect(pantalla, shadow_color, shadow_rect, border_radius=border_radius)
        pygame.draw.rect(pantalla, input_bg_color, self.input_rect, border_radius=border_radius)
        # Actualizar botón enviar
        self.boton_enviar.x = self.input_rect.right - self.btn_size
        self.boton_enviar.y = self.input_rect.y + (self.input_rect.height - self.btn_size) // 2
        self.boton_enviar.ancho = self.btn_size
        self.boton_enviar.alto = self.btn_size
        self.boton_enviar.texto_visible = False
        activo = self.texto_usuario.strip() and not esperando_respuesta
        color = (255, 120, 120) if activo else (240, 240, 245)
        self.boton_enviar.color_top = self.boton_enviar.color_bottom = self.boton_enviar.color_hover = color
        self.boton_enviar.draw(pantalla)
        # Actualizar botón voz
        self.boton_voz.x = self.input_rect.x + 8
        self.boton_voz.y = self.input_rect.y + (self.input_rect.height - self.btn_size) // 2
        self.boton_voz.ancho = self.btn_size
        self.boton_voz.alto = self.btn_size
        self.draw_voice_button(pantalla)
        # Ajustar márgenes para el área de texto
        text_area_right = self.boton_enviar.x - 16
        text_area_left = self.boton_voz.x + self.boton_voz.ancho + 8  # margen después del botón voz
        color_texto = (120, 120, 120) if self.texto_usuario else (180, 180, 185)
        text_x = text_area_left
        text_y = self.input_rect.y + (self.input_rect.height - self.font.get_height()) // 2
        max_text_width = text_area_right - text_x
        pre_cursor = self.texto_usuario[:self.cursor_pos]
        rendered_pre = self.font.render(pre_cursor, True, color_texto)
        rendered_full = self.font.render(self.texto_usuario, True, color_texto)
        scroll_offset = self._calcular_scroll_offset(rendered_pre, rendered_full, max_text_width)
        if self._has_selection():
            start, end = self._get_selection_range()
            pre = self.texto_usuario[:start]
            sel = self.texto_usuario[start:end]
            rendered_pre = self.font.render(pre, True, color_texto)
            rendered_sel = self.font.render(sel, True, color_texto)
            sel_x = text_x + rendered_pre.get_width() - scroll_offset
            sel_w = rendered_sel.get_width()
            sel_rect = pygame.Rect(sel_x, text_y, sel_w, self.font.get_height())
            pygame.draw.rect(pantalla, (200, 220, 255), sel_rect)
        superficie = self.font.render(self.texto_usuario, True, color_texto)
        visible_rect = pygame.Rect(scroll_offset, 0, max_text_width, superficie.get_height())
        pantalla.blit(superficie, (text_x, text_y), area=visible_rect)
        if not self.texto_usuario:
            placeholder = "Escribe un mensaje..."
            placeholder_color = (200, 200, 210)
            placeholder_surf = self.font.render(placeholder, True, placeholder_color)
            pantalla.blit(placeholder_surf, (text_x, text_y))
        if self.cursor_visible and not esperando_respuesta:
            cursor_x = text_x + rendered_pre.get_width() - scroll_offset
            cursor_y = text_y
            cursor_h = superficie.get_height()
            if cursor_x < text_area_right:
                pygame.draw.line(pantalla, (255, 120, 120), (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_h), 2)
            if not self.texto_usuario:
                pygame.draw.line(pantalla, (255, 120, 120), (text_x, cursor_y), (text_x, cursor_y + cursor_h), 2)

    def draw_loading_bar(self, pantalla):
        border_radius = self.input_rect.height // 2
        bar_thickness = self._loading_border_thickness
        rect = self.input_rect.inflate(bar_thickness*2, bar_thickness*2)
        if self._loading_border_last_rect is None or self._loading_border_last_rect.size != rect.size or self._loading_border_last_rect.topleft != rect.topleft:
            self._update_loading_border_points()
        time_ms = pygame.time.get_ticks()
        perimeter = self._loading_border_perimeter
        progress = (time_ms // 3) % perimeter
        chunk_len = self._loading_border_chunk_len
        color1, color2 = self._loading_border_colors
        pygame.draw.rect(pantalla, (230, 230, 230), rect, width=bar_thickness, border_radius=border_radius+2)
        for i in range(chunk_len):
            idx = (progress + i) % perimeter
            fade = i / chunk_len
            color = (
                int(color1[0] + (color2[0] - color1[0]) * fade),
                int(color1[1] + (color2[1] - color1[1]) * fade),
                int(color1[2] + (color2[2] - color1[2]) * fade)
            )
            x, y = self._loading_border_points[idx]
            pygame.draw.circle(pantalla, color, (int(x), int(y)), bar_thickness//2+1)

    def update_layout(self, input_rect, font):
        self.input_rect = input_rect
        self.font = font
        self.btn_size = min(self.input_rect.height - 2, self.scaler.scale_x_value(48))
        self._init_buttons(self.boton_enviar.on_click)
        self._update_loading_border_points()

    def clear_input(self):
        self.texto_usuario = ""
        self.cursor_pos = 0
        self.selection_start = 0
        self.selection_end = 0
        self._undo_stack.clear()

    def get_text(self):
        return self.texto_usuario

    def set_cursor_visible(self, visible):
        self.cursor_visible = visible

    def draw_voice_button(self, pantalla):
        """Dibuja el botón de voz con el color adecuado según si hay mensaje de IA disponible."""
        enabled = self._hay_mensaje_ia()
        if enabled:
            colores = {
                'color_top': (120, 200, 255),
                'color_bottom': (180, 240, 255),
                'color_hover': (100, 180, 220)
            }
        else:
            colores = {
                'color_top': (200, 200, 200),
                'color_bottom': (200, 200, 200),
                'color_hover': (200, 200, 200)
            }
        for attr, value in colores.items():
            setattr(self.boton_voz, attr, value)
        self.boton_voz.draw(pantalla)

    def handle_voice_event(self, event):
        """Encapsula el manejo de eventos del botón de voz."""
        self.boton_voz.handle_event(event)
