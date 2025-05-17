class ChatbotStateManager:
    def __init__(self, max_visible=10):
        self.all_messages = []          # Lista con todos los mensajes (ilimitada)
        self.max_visible = max_visible  # Cantidad máxima de mensajes a mostrar
        self.visible_start = 0          # Índice del primer mensaje visible
        self.needs_redraw = True        # Indica si hay que redibujar
        self.scroll_offset_px = 0       # Desplazamiento vertical en píxeles
        self._mensajes_altos = []       # Altura de cada mensaje (actualizado por UI)

    def add_message(self, text):
        """Agrega un mensaje a la lista total y ajusta la ventana de mensajes visibles."""
        self.all_messages.append(text)
        # Si estamos al final, mueve la ventana para mostrar el nuevo mensaje
        if self.visible_start + self.max_visible >= len(self.all_messages) - 1:
            self.visible_start = max(0, len(self.all_messages) - self.max_visible)
        self.needs_redraw = True

    def clear(self):
        """Limpia todos los mensajes."""
        self.all_messages.clear()
        self.visible_start = 0
        self.scroll_offset_px = 0
        self._mensajes_altos = []
        self.needs_redraw = True

    def get_messages(self):
        """Devuelve solo los mensajes actualmente visibles."""
        end = self.visible_start + self.max_visible
        return self.all_messages[self.visible_start:end]

    def scroll_up(self):
        """Desplaza la ventana de mensajes hacia arriba."""
        if self.visible_start > 0:
            self.visible_start -= 1
            self.needs_redraw = True

    def scroll_down(self):
        """Desplaza la ventana de mensajes hacia abajo."""
        if self.visible_start + self.max_visible < len(self.all_messages):
            self.visible_start += 1
            self.needs_redraw = True

    def mark_drawn(self):
        self.needs_redraw = False

    def should_redraw(self):
        return self.needs_redraw

    # --- Integración con scroll visual (en píxeles) ---
    def set_mensajes_altos(self, altos):
        """Recibe una lista con la altura de cada mensaje (en píxeles). Llamar desde el renderizado."""
        self._mensajes_altos = altos

    def get_total_height(self):
        """Devuelve la altura total de todos los mensajes (en píxeles)."""
        return sum(self._mensajes_altos) if self._mensajes_altos else 0

    def set_scroll_offset_px(self, offset):
        """Establece el desplazamiento vertical en píxeles (desde la UI/ScrollManager)."""
        self.scroll_offset_px = max(0, min(offset, max(0, self.get_total_height() - 1)))

    def get_visible_messages_by_scroll(self, area_height):
        """Devuelve los mensajes y el offset inicial para renderizar según scroll_offset_px y alto del área visible."""
        if not self._mensajes_altos or not self.all_messages:
            return [], 0
        start_px = self.scroll_offset_px
        y = 0
        start_idx = 0
        # Buscar el primer mensaje visible
        for i, alto in enumerate(self._mensajes_altos):
            if y + alto > start_px:
                start_idx = i
                break
            y += alto
        # Acumular mensajes hasta llenar el área visible
        mensajes = []
        offset_inicial = y - start_px
        y_actual = y
        for i in range(start_idx, len(self.all_messages)):
            if y_actual - start_px >= area_height:
                break
            mensajes.append((self.all_messages[i], self._mensajes_altos[i]))
            y_actual += self._mensajes_altos[i]
        return mensajes, offset_inicial

    def replace_last_bot_message(self, new_message):
        """Reemplaza el último mensaje del bot con uno nuevo"""
        for i in range(len(self.all_messages) - 1, -1, -1):
            if self.all_messages[i][0] == "bot":
                self.all_messages[i] = ("bot", new_message)
                self.needs_redraw = True
                return True
        return False