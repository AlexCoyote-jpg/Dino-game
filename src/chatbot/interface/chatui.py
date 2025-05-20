import pygame
import threading
from ui.components.utils import dibujar_caja_texto
from chatbot.chat import ChatBot
from ui.components.scroll import ScrollManager, dibujar_barra_scroll
from core.scale.responsive_scaler_basic import ResponsiveScaler
from chatbot.interface.chat_utils import wrap_text
from chatbot.interface.chat_render import draw_burbuja, render_chat
from chatbot.interface.chat_scroll import calcular_offset_ultimo_usuario
from chatbot.interface.chat_input import ChatInputManager

BUBBLE_PADDING = 14
MIN_THUMB_HEIGHT = 30
LINE_SPACING = 0  # El espaciado vertical lo controlamos con el alto de línea real

class BotScreen:
    def __init__(self, menu):
        self.menu = menu
        self.chatbot = ChatBot()
        self._hist_lock = threading.Lock()
        BASE_WIDTH, BASE_HEIGHT = 800, 600
        self.scaler = ResponsiveScaler(base_width=BASE_WIDTH, base_height=BASE_HEIGHT)
        self.last_screen_size = (0, 0)
        screen_width, screen_height = self.menu.pantalla.get_width(), self.menu.pantalla.get_height()
        self.input_rect = pygame.Rect(
            self.scaler.scale_x_value(100),
            self.scaler.scale_y_value(520),
            screen_width - self.scaler.scale_x_value(200),
            self.scaler.scale_y_value(50)
        )
        self.font = pygame.font.Font(None, 28)
        self.titulo_surface = self.font.render("🦖 DinoBot", True, (70, 130, 180))
        self._last_typing_index = -1
        self.scroll_manager = ScrollManager()
        self._mensajes_altos = []
        self._total_chat_height = 0
        self._thumb_rect = None
        self._render_cache = []
        self._scroll_offset = 0
        self.typing_animation_index = 0
        self.esperando_respuesta = False
        self.auto_scroll_enabled = True
        self.smooth_scroll = True
        self._layout_dirty = True
        self._render_cache_dirty = True
        # Solo una llamada a _update_layout aquí
        self.input_manager = ChatInputManager(
            self.scaler, self.input_rect, self.font, self.enviar_mensaje, chatbot=self.chatbot
        )
        self._update_layout(force=True)

    def _update_layout(self, force=False, before_input_manager=False):
        current_size = self.menu.pantalla.get_size()
        if not (force or current_size != self.last_screen_size):
            return
        prev_chat_h = getattr(self, 'chat_h', None)
        prev_total_height = getattr(self, '_total_chat_height', 0)
        prev_scroll_offset = getattr(self, '_scroll_offset', 0)
        self.last_screen_size = current_size
        self.scaler.update(*current_size)
        screen_width, screen_height = current_size
        self.input_rect = pygame.Rect(
            self.scaler.scale_x_value(100),
            self.scaler.scale_y_value(520),
            screen_width - self.scaler.scale_x_value(200),
            self.scaler.scale_y_value(50)
        )
        self.chat_x = self.scaler.scale_x_value(100)
        self.chat_y = self.scaler.scale_y_value(120)
        self.chat_w = screen_width - self.scaler.scale_x_value(200)
        self.chat_h = self.scaler.scale_y_value(380)
        font_size = self.scaler.scale_font_size(28)
        self.font = pygame.font.Font(None, font_size)
        self.titulo_surface = self.font.render("🦖 DinoBot", True, (70, 130, 180))
        if not before_input_manager:
            self.input_manager.update_layout(self.input_rect, self.font)
        self._layout_dirty = True
        self._render_cache_dirty = True
        # --- Mejora de scroll al redimensionar hacia arriba ---
        if prev_chat_h is not None and self.chat_h > prev_chat_h and prev_total_height > 0:
            max_scroll_old = max(0, prev_total_height - prev_chat_h)
            max_scroll_new = max(0, prev_total_height - self.chat_h)
            if abs(prev_scroll_offset - max_scroll_old) < 2:
                self.scroll_manager.target_scroll = max_scroll_new
                self.scroll_manager.scroll_pos = max_scroll_new
            else:
                rel = prev_scroll_offset / max(1, max_scroll_old)
                # Clamp robusto
                rel = min(max(rel, 0.0), 1.0)
                self.scroll_manager.target_scroll = int(rel * max_scroll_new)
                self.scroll_manager.scroll_pos = int(rel * max_scroll_new)

    def enviar_mensaje(self):
        mensaje = self.input_manager.get_text().strip()
        if mensaje and not self.esperando_respuesta:
            self.esperando_respuesta = True
            self.input_manager.clear_input()
            self._render_cache_dirty = True
            threading.Thread(target=self._procesar_en_hilo, args=(mensaje,), daemon=True).start()

    def _procesar_en_hilo(self, mensaje):
        self.chatbot.procesar_input(mensaje)
        self.esperando_respuesta = False
        self._render_cache_dirty = True
        target_offset = self._calcular_offset_ultimo_usuario()
        if self.auto_scroll_enabled and abs(target_offset - self._scroll_offset) > 5:
            instant = not self.smooth_scroll
            self.scroll_manager.scroll_to_bottom(target_offset, instant=instant)

    def _calcular_offset_ultimo_usuario(self):
        historial = self.chatbot.obtener_historial()
        return calcular_offset_ultimo_usuario(
            historial, self.font, self.chat_w, self._total_chat_height, self.chat_h
        )

    def handle_event(self, event):
        if self.input_manager.handle_event(event, self.esperando_respuesta) == 'send':
            self.enviar_mensaje()
            return
        bar_rect = pygame.Rect(self.chat_x + self.chat_w - 18, self.chat_y, 16, self.chat_h)
        max_scroll = max(0, self._total_chat_height - self.chat_h)
        scroll_step = self.font.get_linesize() * 2
        page_step = self.chat_h - self.font.get_linesize() * 2
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.scroll_manager.scroll_by(scroll_step)
            elif event.key == pygame.K_UP:
                self.scroll_manager.scroll_by(-scroll_step)
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_manager.scroll_by(page_step)
            elif event.key == pygame.K_PAGEUP:
                self.scroll_manager.scroll_by(-page_step)
            elif event.key == pygame.K_END:
                self.scroll_manager.scroll_to(max_scroll)
            elif event.key == pygame.K_HOME:
                self.scroll_manager.scroll_to(0)
        self.scroll_manager.handle_event(event, 40, self._thumb_rect, max_scroll, self.chat_h, self.chat_y, bar_rect)

    def _actualizar_render_cache(self):
        with self._hist_lock:
            historial = self.chatbot.obtener_historial()[-100:]
        if not historial:
            self._render_cache = []
            self._mensajes_altos = []
            self._total_chat_height = 0
            self._layout_dirty = False
            self._render_cache_dirty = False
            return
        mensajes, alturas = [], []
        ancho_texto = self.chat_w - 40
        font = self.font
        esperando = self.esperando_respuesta
        typing_index = self.typing_animation_index
        for autor, texto in historial:
            if not isinstance(texto, str):
                continue
            if autor == "bot":
                color_texto = (70, 130, 180)
                bg_color = (230, 240, 255)
                alineacion = "izq"
                if texto == "" and esperando:
                    texto = f"Escribiendo{'.' * typing_index}"
            else:
                color_texto = (0, 0, 0)
                bg_color = (255, 255, 255)
                alineacion = "der"
            for linea in wrap_text(texto, font, ancho_texto):
                mensajes.append((linea, color_texto, bg_color, alineacion))
                line_height = font.size(linea)[1] + max(8, int(font.get_linesize() * 0.25)) * 2
                alturas.append(line_height)
        # Solo marca dirty si realmente cambió el contenido
        if mensajes != self._render_cache or alturas != self._mensajes_altos:
            self._render_cache = mensajes
            self._mensajes_altos = alturas
            self._total_chat_height = sum(alturas)
        self._layout_dirty = False
        self._render_cache_dirty = False

    def update(self, dt):
        max_scroll = max(0, self._total_chat_height - self.chat_h)
        # Clamp robusto
        self.scroll_manager.target_scroll = max(0, min(self.scroll_manager.target_scroll, max_scroll))
        self.scroll_manager.scroll_pos = max(0, min(self.scroll_manager.scroll_pos, max_scroll))
        self._scroll_offset = self.scroll_manager.update(max_scroll, smooth=True)
        self.input_manager.update()
        if self.esperando_respuesta:
            now = pygame.time.get_ticks()
            typing_index = (now // 300) % 4
            if typing_index != self._last_typing_index:
                self.typing_animation_index = typing_index
                self._render_cache_dirty = True
                self._last_typing_index = typing_index

    def draw(self, pantalla):
        self._update_layout()
        if self._layout_dirty or self._render_cache_dirty:
            self._actualizar_render_cache()
        pantalla.blit(self.titulo_surface, (self.chat_x, self.scaler.scale_y_value(40)))
        def draw_burbuja_cb(pantalla, linea, color, bg, ali, y):
            self._draw_burbuja(pantalla, linea, color, bg, ali, y)
        render_chat.draw_burbuja_cb = draw_burbuja_cb
        thumb_rect_ref = [self._thumb_rect]
        render_chat(
            pantalla,
            self.chat_x,
            self.chat_y,
            self.chat_w,
            self.chat_h,
            self.font,
            self._scroll_offset,
            self._render_cache,
            self._total_chat_height,
            thumb_rect_ref,
            self._mensajes_altos
        )
        self._thumb_rect = thumb_rect_ref[0]
        self.input_manager.draw(pantalla, self.esperando_respuesta)
        if self.esperando_respuesta:
            self.input_manager.draw_loading_bar(pantalla)

    def _draw_burbuja(self, pantalla, linea, color, bg, ali, y):
        draw_burbuja(pantalla, self.font, self.chat_x, self.chat_w, linea, color, bg, ali, y)

    def stop_audio(self):
        if self.input_manager._voz_reproduciendo:
            if self.chatbot:
                self.chatbot.detener_audio()
            self.input_manager._voz_reproduciendo = False
            # Aquí puedes agregar lógica adicional para detener el audio si es necesario