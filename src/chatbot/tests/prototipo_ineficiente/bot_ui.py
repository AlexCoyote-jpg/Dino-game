import pygame
import sys
import textwrap
import logging
import time
from collections import OrderedDict
from functools import lru_cache
from chatbot.Configs import LLAMA
from chatbot.Conexion import obtener_respuesta_async
from chatbot.voz import hablar, detener
from ui.components.utils import obtener_fuente, render_text_cached, Boton
from ui.components.scroll import ScrollManager, dibujar_barra_scroll
from ui.components.emoji import mostrar_alternativo_adaptativo, get_emoji_renderer
from chatbot.tests.prototipo_ineficiente.event_handlers import (
    hay_respuesta_bot,
    manejar_voz,
    procesar_mensaje_async,
    respuesta_callback,
    handle_key_event,
    handle_mouse_event,
    process_events
)
from core.scale.responsive_scaler_basic import ResponsiveScaler
from chatbot.chatbot_state import ChatbotStateManager

# Inicialización de pygame
pygame.init()
pygame.mixer.init()

# Sistema de escalado responsivo
scaler = ResponsiveScaler(base_width=900, base_height=600)

# Sistema de caché LRU optimizado para redimensionamiento
class ResizableLRUCache:
    """
    Caché LRU con soporte para redimensionamiento y gestión eficiente de memoria.
    Limpia automáticamente los elementos según tamaño cuando cambia la resolución.
    """
    def __init__(self, capacity=50, name="default"):
        self.cache = OrderedDict()
        self.capacity = max(10, capacity)
        self.name = name
        self.size_key = None  # Clave de tamaño actual
        self.hits = 0
        self.misses = 0
        self.last_cleanup = time.time()
    
    def get(self, key, size_key=None):
        """Obtiene un elemento del caché, verificando compatibilidad de tamaño"""
        # Usar tamaño actual si no se especifica
        current_size = size_key or self.size_key
        
        # Verificar si la clave existe y es compatible con el tamaño actual
        cache_key = (key, current_size)
        if cache_key in self.cache:
            self.hits += 1
            self.cache.move_to_end(cache_key)
            return self.cache[cache_key]
        
        self.misses += 1
        return None
    
    def put(self, key, value, size_key=None):
        """Almacena un elemento en caché con información de tamaño"""
        # Usar tamaño actual si no se especifica
        current_size = size_key or self.size_key
        
        # Almacenar en caché
        cache_key = (key, current_size)
        self.cache[cache_key] = value
        self.cache.move_to_end(cache_key)
        
        # Controlar tamaño máximo
        while len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
    
    def clear(self):
        """Limpia todo el caché"""
        self.cache.clear()
    
    def set_size_key(self, width, height):
        """Establece la clave de tamaño actual y limpia entradas incompatibles"""
        old_size_key = self.size_key
        self.size_key = (width, height)
        
        # Si el tamaño ha cambiado significativamente, limpiar entradas incompatibles
        if old_size_key and self.size_key:
            old_w, old_h = old_size_key
            new_w, new_h = self.size_key
            
            # Solo limpiar si el cambio es sustancial (>20%) y ha pasado suficiente tiempo
            if (time.time() - self.last_cleanup > 0.5 and
                (abs(old_w - new_w) / old_w > 0.2 or abs(old_h - new_h) / old_h > 0.2)):
                
                # Filtrar entradas obsoletas
                new_cache = OrderedDict()
                for (k, sz), v in self.cache.items():
                    if sz == self.size_key:
                        new_cache[(k, sz)] = v
                
                self.cache = new_cache
                self.last_cleanup = time.time()
                logging.debug(f"Caché '{self.name}' limpiado por cambio de tamaño: {old_size_key} -> {self.size_key}")

# Cachés optimizadas para diferentes tipos de recursos
_avatar_cache = ResizableLRUCache(capacity=30, name="avatars")
_button_cache = ResizableLRUCache(capacity=20, name="buttons")
_text_cache = ResizableLRUCache(capacity=100, name="text")
_surface_cache = ResizableLRUCache(capacity=5, name="surfaces")

# Estado global
state = {
    'entrada_usuario': "",
    'esperando_respuesta': False,
    'theme': 'light',  # Tema actual (light/dark)
    'resize_event': {
        'timestamp': 0,
        'width': 900,
        'height': 600
    }
}

# Historial y scroll
historial = ChatbotStateManager(max_visible=15)
scroll_manager = ScrollManager()

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

# Temas visuales (claro/oscuro)
THEMES = {
    'light': {
        "COLOR_FONDO": (248, 249, 250),
        "COLOR_TEXTO": (33, 37, 41),
        "COLOR_ENTRADA": (255, 255, 255),
        "COLOR_BOT": (240, 242, 245),
        "COLOR_USER": (0, 123, 255),
        "COLOR_USER_TEXT": (255, 255, 255),
        "COLOR_BOT_TEXT": (33, 37, 41),
        "COLOR_LINEA": (220, 220, 220),
    },
    'dark': {
        "COLOR_FONDO": (25, 25, 30),
        "COLOR_TEXTO": (220, 220, 220),
        "COLOR_ENTRADA": (45, 45, 50),
        "COLOR_BOT": (50, 50, 60),
        "COLOR_USER": (0, 90, 180),
        "COLOR_USER_TEXT": (240, 240, 240),
        "COLOR_BOT_TEXT": (220, 220, 220),
        "COLOR_LINEA": (70, 70, 80),
    }
}

# Lista de mensajes de bienvenida por defecto
DEFAULT_WELCOME_MESSAGES = [
    "Bot: Hola 👋 Soy tu asistente. ¿En qué puedo ayudarte hoy?"
]

def initialize_chatbot(welcome_messages=None):
    """
    Inicializa el chatbot con mensajes de bienvenida.
    
    Args:
        welcome_messages: Lista opcional de mensajes de bienvenida.
                         Si es None, se usará DEFAULT_WELCOME_MESSAGES.
    """
    historial.clear()
    messages = welcome_messages or DEFAULT_WELCOME_MESSAGES
    for message in messages:
        historial.add_message(message)
    return historial

def set_theme(theme_name):
    """
    Cambia el tema del chatbot entre 'light' y 'dark'.
    
    Args:
        theme_name: Nombre del tema ('light' o 'dark')
    """
    if theme_name in THEMES:
        state['theme'] = theme_name
        # Limpiar caché de superficies para forzar redibujado
        _surface_cache.clear()

@lru_cache(maxsize=8)
def _get_theme_constants(theme_name):
    """Obtiene las constantes de color para el tema actual (con caché)"""
    return THEMES.get(theme_name, THEMES['light'])

def set_render_area(width, height):
    """
    Actualiza el escalador con las nuevas dimensiones y gestiona cachés.
    Notifica del cambio de tamaño al sistema de caché.
    
    Args:
        width: Nuevo ancho de área
        height: Nuevo alto de área
    """
    # Actualizar escalador
    old_width, old_height = scaler.current_width, scaler.current_height
    scaler.update(width, height)
    
    # Registrar evento de cambio de tamaño
    state['resize_event'] = {
        'timestamp': time.time(),
        'width': width,
        'height': height,
        'changed': abs(old_width - width) > 5 or abs(old_height - height) > 5
    }
    
    # Actualizar cachés con el nuevo tamaño
    _avatar_cache.set_size_key(width, height)
    _button_cache.set_size_key(width, height)
    _text_cache.set_size_key(width, height)
    _surface_cache.set_size_key(width, height)
    
    # Limpiar caché de texto renderizado si existe
    if 'render_text_cached' in globals() and hasattr(globals()['render_text_cached'], 'cache'):
        globals()['render_text_cached'].cache.clear()

def get_visual_constants():
    """
    Obtiene constantes visuales adaptadas al tamaño actual.
    Combina constantes de diseño con tema de color actual.
    """
    current_width = scaler.current_width
    current_height = scaler.current_height
    
    # Constantes básicas
    constants = {
        "ANCHO": current_width,
        "ALTO": current_height,
        "FUENTE": pygame.font.SysFont("Segoe UI Emoji", scaler.scale_font_size(25)),
        "LINE_HEIGHT": scaler.scale_y_value(32),
        "MAX_LINE_WIDTH": 60,
        "BORDER_RADIUS": max(8, scaler.scale_x_value(18)),
        "MENSAJE_SOMBRA": scaler.scale_x_value(3),
        "SCROLL_WIDTH": max(6, scaler.scale_x_value(8)),
        "SCROLL_MARGIN": scaler.scale_x_value(2),
        "RESPUESTA_ANIMACION_VELOCIDAD": 4,
        "AVATAR_SIZE": max(20, scaler.scale_x_value(32)),
    }
    
    # Añadir colores según tema actual
    theme_colors = _get_theme_constants(state['theme'])
    constants.update(theme_colors)
    
    return constants

def get_avatar_surface(label, color):
    """
    Obtiene o genera la superficie del avatar con soporte para redimensionamiento.
    
    Args:
        label: Texto/emoji para el avatar
        color: Color de fondo (RGB)
        
    Returns:
        Surface: Avatar renderizado
    """
    # Obtener constantes visuales actuales
    size = get_visual_constants()["AVATAR_SIZE"]
    
    # Crear clave única para este avatar en este tamaño
    key = (label, tuple(color))  # Asegurar que color sea una tupla hasheable
    
    # Verificar caché
    avatar = _avatar_cache.get(key)
    if avatar is not None:
        return avatar
    
    # Crear nueva superficie de avatar
    radius = size // 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Dibujar círculo de fondo
    pygame.draw.circle(surf, color, (radius, radius), radius)
    
    # Escalar el emoji al tamaño apropiado
    emoji_size = max(12, int(size * 0.6))
    
    # Intentar usar primero el sistema de emojis avanzado
    try:
        renderer = get_emoji_renderer()
        renderer.render_line(surf, label, 0, 0, emoji_size, (255, 255, 255), 
                            centered=True, max_width=size)
    except (ImportError, AttributeError):
        # Fallback: usar render_text_cached
        try:
            emoji = render_text_cached(label, emoji_size, False, (255, 255, 255))
            surf.blit(emoji, emoji.get_rect(center=(radius, radius)))
        except Exception as e:
            # Último recurso: dibujar un simple círculo de color
            logging.warning(f"Error al renderizar avatar {label}: {e}")
    
    # Guardar en caché y devolver
    _avatar_cache.put(key, surf)
    return surf

@lru_cache(maxsize=32)
def _get_font_size_limits(area_width):
    """Determina límites de tamaño de fuente según ancho de área (con caché)"""
    if area_width < 400:
        return (13, 20)  # Tamaños para pantallas muy pequeñas
    elif area_width < 700:
        return (16, 24)  # Tamaños para pantallas pequeñas
    else:
        return (20, 32)  # Tamaños para pantallas normales/grandes

def render_emoji_button(emoji, min_size=28):
    """
    Renderiza un emoji para usar como botón con tamaño adaptativo.
    
    Args:
        emoji: Emoji a renderizar
        min_size: Tamaño mínimo garantizado
        
    Returns:
        Surface: Icono de botón renderizado
    """
    # Determinar tamaño ideal según escalado actual
    size = max(min_size, scaler.scale_font_size(40))
    
    # Verificar caché
    key = emoji
    button = _button_cache.get(key)
    if button is not None:
        return button
    
    # Intentar usar el renderizador de emojis avanzado
    try:
        renderer = get_emoji_renderer()
        btn_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        renderer.render_line(btn_surf, emoji, 0, 0, size, (28, 28, 30), 
                          centered=True, max_width=size)
    except (ImportError, AttributeError):
        # Fallback: usar render_text_cached
        try:
            # Crear una fuente del tamaño adecuado
            font = pygame.font.SysFont("Segoe UI Emoji", size)
            
            # Renderizar el emoji
            render = font.render(emoji, True, (28, 28, 30))
            
            # Verificar si necesita escalado
            if render.get_width() < min_size or render.get_height() < min_size:
                min_dim = max(render.get_width(), render.get_height(), 1)
                scale_factor = min_size / min_dim
                render = pygame.transform.smoothscale(
                    render, 
                    (max(1, int(render.get_width() * scale_factor)),
                     max(1, int(render.get_height() * scale_factor)))
                )
            
            # Crear superficie final
            btn_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            btn_surf.blit(render, render.get_rect(center=(size//2, size//2)))
        except Exception as e:
            # Si falla, crear una superficie simple
            logging.warning(f"Error al renderizar botón {emoji}: {e}")
            btn_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(btn_surf, (100, 100, 255), (size//2, size//2), size//2)
    
    # Guardar en caché y devolver
    _button_cache.put(key, btn_surf)
    return btn_surf

# Caché de botones para evitar recreación constante
_cached_buttons = None
_cached_buttons_timestamp = 0

def get_botones():
    """
    Genera o recupera botones para la interfaz, optimizado con caché.
    Se regeneran solo cuando cambia el tamaño o ha pasado tiempo suficiente.
    
    Returns:
        list: Lista de objetos Boton
    """
    global _cached_buttons, _cached_buttons_timestamp
    
    # Verificar si necesitamos regenerar botones
    current_time = time.time()
    resize_event = state['resize_event']
    
    # Reutilizar botones si no han pasado más de 2 segundos y no hubo cambio de tamaño
    if (_cached_buttons and current_time - _cached_buttons_timestamp < 2.0 
            and (not resize_event['changed'] or current_time - resize_event['timestamp'] > 0.5)):
        return _cached_buttons
    
    # Registrar tiempo de generación
    _cached_buttons_timestamp = current_time
    
    # Obtener constantes visuales actuales
    c = get_visual_constants()
    sx = scaler.scale_x_value
    sy = scaler.scale_y_value
    ANCHO, ALTO = c["ANCHO"], c["ALTO"]
    
    # Adaptar tamaño de botones según resolución
    is_small_screen = ANCHO < 450
    button_size = max(35, min(48, sx(48)))
    button_spacing = max(30, sx(40))
    
    # Calcular posiciones según tamaño de pantalla
    if is_small_screen:
        # Pantalla pequeña: agrupar botones a la derecha
        base_x = ANCHO - button_size - sx(20)
        base_y = ALTO - sy(55)
        offsets = [
            (0, 0),  # Enviar
            (-button_spacing, 0),  # Voz
            (-button_spacing*2, 0),  # Limpiar
        ]
    else:
        # Pantalla normal: botones espaciados
        base_x = ANCHO - button_size - sx(30)
        base_y = ALTO - sy(55)
        offsets = [
            (0, 0),  # Enviar
            (-button_spacing, 0),  # Voz
            (-button_spacing*2, 0),  # Limpiar
        ]
    
    # Crear botones con posiciones adaptativas
    buttons = [
        # Botón Enviar
        Boton(
            texto="",
            x=base_x + offsets[0][0], 
            y=base_y + offsets[0][1], 
            ancho=button_size, 
            alto=button_size,
            id="enviar",
            imagen=render_emoji_button("📤"),
            imagen_pos="center",
            color_normal=(240, 240, 255),
            color_hover=(200, 220, 255),
            color_top=(180, 210, 255),
            color_bottom=(120, 170, 255),
            border_color=(180, 200, 255, 180),
            border_width=max(1, sx(2)),
            border_radius=max(8, min(30, sx(20))),
            estilo="apple",
            tooltip="Enviar mensaje",
            on_click=lambda: procesar_mensaje_async(state, historial, lambda r: respuesta_callback(r, historial, state))
        ),
        # Botón Voz
        Boton(
            texto="",
            x=base_x + offsets[1][0], 
            y=base_y + offsets[1][1], 
            ancho=button_size, 
            alto=button_size,
            id="voz",
            imagen=render_emoji_button("🔊"),
            imagen_pos="center",
            color_normal=(240, 255, 240),
            color_hover=(200, 255, 200),
            color_top=(180, 255, 210),
            color_bottom=(120, 170, 255),
            border_color=(180, 220, 180, 180),
            border_width=max(1, sx(2)),
            border_radius=max(8, min(18, sx(15))),
            estilo="apple",
            tooltip="Reproducir voz",
            on_click=lambda: manejar_voz(historial)
        ),
        # Botón Limpiar
        Boton(
            texto="",
            x=base_x + offsets[2][0], 
            y=base_y + offsets[2][1], 
            ancho=button_size, 
            alto=button_size,
            id="limpiar",
            imagen=render_emoji_button("🧹"),
            tooltip="Limpiar historial",
            estilo="apple",
            on_click=lambda: historial.clear()
        ),
    ]
    
    # Actualizar caché de botones
    _cached_buttons = buttons
    return buttons

def recortar_texto_eficiente(texto, font, max_width, ellipsis="…"):
    """
    Recorta texto para que quepa en un ancho máximo, usando búsqueda binaria.
    
    Args:
        texto: Texto a recortar
        font: Fuente para medir el texto
        max_width: Ancho máximo en píxeles
        ellipsis: Carácter para indicar texto truncado
        
    Returns:
        tuple: (texto_recortado, fue_truncado)
    """
    # Verificar caché primero
    key = (texto, id(font), max_width)
    cached = _text_cache.get(key)
    if cached is not None:
        return cached
    
    # Si el texto completo cabe, devolverlo directamente
    if font.size(texto)[0] <= max_width:
        result = (texto, False)
        _text_cache.put(key, result)
        return result
    
    # Si ni siquiera cabe el ellipsis, devolver solo eso
    if font.size(ellipsis)[0] >= max_width:
        result = (ellipsis, True)
        _text_cache.put(key, result)
        return result
    
    # Búsqueda binaria para encontrar punto de corte óptimo
    ellipsis_width = font.size(ellipsis)[0]
    available_width = max_width - ellipsis_width
    
    # Búsqueda binaria
    left, right = 0, len(texto) - 1
    while left <= right:
        mid = (left + right) // 2
        if font.size(texto[:mid])[0] <= available_width:
            left = mid + 1
        else:
            right = mid - 1
    
    # Construir texto truncado
    truncated = texto[:max(0, right)] + ellipsis
    result = (truncated, True)
    
    # Guardar en caché y devolver
    _text_cache.put(key, result)
    return result

def renderizar_historial(pantalla):
    """
    Renderiza el historial de mensajes con soporte optimizado para redimensionamiento.
    
    Args:
        pantalla: Superficie donde dibujar
        
    Returns:
        tuple: (superficies_renderizadas, altura_total)
    """
    # Obtener constantes visuales actuales
    c = get_visual_constants()
    sx, sy = scaler.scale_x_value, scaler.scale_y_value
    FUENTE = c["FUENTE"]
    LINE_HEIGHT, MAX_LINE_WIDTH = c["LINE_HEIGHT"], c["MAX_LINE_WIDTH"]
    BORDER_RADIUS = c["BORDER_RADIUS"]
    MENSAJE_SOMBRA = c["MENSAJE_SOMBRA"]
    SCROLL_WIDTH = c["SCROLL_WIDTH"]
    SCROLL_MARGIN = c["SCROLL_MARGIN"]
    ANCHO, ALTO = c["ANCHO"], c["ALTO"]
    
    # Calcular dimensiones del área de scroll
    margin_horiz = sx(20)
    spacing = sy(10)
    avatar_margin = sx(40)
    
    # Área de scroll
    SCROLL_AREA = pygame.Rect(
        margin_horiz, 
        sy(20), 
        ANCHO - margin_horiz * 2 - SCROLL_WIDTH - SCROLL_MARGIN, 
        int(ALTO * 0.7)
    )
    
    # Obtener mensajes del historial
    mensajes = historial.all_messages if hasattr(historial, 'all_messages') else historial
    
    # --- Calcular altura de cada mensaje (para scroll pixel-perfect) ---
    alturas = []
    mensajes_renders = []
    
    # Limitar procesamiento a mensajes recientes si hay demasiados
    max_messages_to_process = 50  # Limitar para mejor rendimiento
    mensajes_to_process = mensajes[-max_messages_to_process:] if len(mensajes) > max_messages_to_process else mensajes
    
    # Procesar cada mensaje
    font_size_min, font_size_max = _get_font_size_limits(ANCHO)
    
    for mensaje in mensajes_to_process:
        is_bot = mensaje.startswith("Bot: ")
        display_msg = ("🤖 " + mensaje[5:]) if is_bot else mensaje
        color = c["COLOR_BOT"] if is_bot else c["COLOR_USER"]
        text_color = c["COLOR_BOT_TEXT"] if is_bot else c["COLOR_USER_TEXT"]
        avatar = get_avatar_surface("🤖" if is_bot else "👤", 
                                   (120,120,220) if is_bot else (52,199,89))
        
        # Optimización: ajustar ancho máximo según tamaño de pantalla
        effective_width = min(80, max(40, MAX_LINE_WIDTH * ANCHO // 900))
        
        # Usar textwrap para dividir el texto en líneas
        lineas = textwrap.wrap(display_msg, effective_width)
        renders = [FUENTE.render(linea, True, text_color) for linea in lineas]
        total_height = len(renders) * (LINE_HEIGHT + sy(4)) - sy(4)
        max_width = max((r.get_width() for r in renders), default=0)
        
        # Calcular dimensiones del mensaje
        padding = max(8, sx(12))
        msg_width = max_width + padding * 2
        msg_height = total_height + padding
        
        # Guardar información para renderizado
        alturas.append(msg_height + spacing)
        mensajes_renders.append((
            mensaje, is_bot, renders, color, text_color,
            avatar, msg_width, msg_height, padding
        ))
    
    # Sincronizar alturas con el gestor de estado
    if hasattr(historial, 'set_mensajes_altos'):
        historial.set_mensajes_altos(alturas)
    
    # --- Obtener mensajes visibles según scroll actual ---
    area_height = SCROLL_AREA.height
    visibles, offset_inicial = [], 0
    
    if hasattr(historial, 'get_visible_messages_by_scroll'):
        # Usar método del gestor de estado si está disponible
        visibles, offset_inicial = historial.get_visible_messages_by_scroll(area_height)
    else:
        # Compatibilidad con versión anterior
        visibles = [(m, h) for m, h in zip(mensajes, alturas)]
        offset_inicial = 0
    
    # --- Renderizar solo mensajes visibles para mejor rendimiento ---
    y_offset = offset_inicial
    surfaces = []
    
    for idx, (mensaje, alto) in enumerate(visibles):
        try:
            i = mensajes.index(mensaje)
            _, is_bot, renders, color, text_color, avatar, msg_width, msg_height, padding = mensajes_renders[i]
        except Exception:
            continue
        
        # Posición del avatar
        x_avatar = avatar_margin if is_bot else SCROLL_AREA.width - avatar.get_width()
        y_avatar = y_offset + (msg_height - avatar.get_height()) // 2
        surfaces.append((avatar, 0 if is_bot else SCROLL_AREA.width - avatar.get_width(), y_avatar, avatar.get_height()))
        
        # Crear superficie para el mensaje
        msg_surface = pygame.Surface((msg_width + MENSAJE_SOMBRA, msg_height + MENSAJE_SOMBRA), pygame.SRCALPHA)
        
        # Dibujar sombra
        pygame.draw.rect(
            msg_surface, 
            (0, 0, 0, 40), 
            pygame.Rect(MENSAJE_SOMBRA, MENSAJE_SOMBRA, msg_width, msg_height), 
            border_radius=BORDER_RADIUS
        )
        
        # Dibujar fondo del mensaje
        pygame.draw.rect(
            msg_surface, 
            color, 
            pygame.Rect(0, 0, msg_width, msg_height), 
            border_radius=BORDER_RADIUS
        )
        
        # Renderizar texto con emojis
        display_text = ("🤖 " + mensaje[5:]) if is_bot else mensaje
        mostrar_alternativo_adaptativo(
            msg_surface,
            display_text,
            padding,
            padding // 2,
            msg_width,
            msg_height,
            color=text_color,
            centrado=False,
            fuente_base=pygame.font.SysFont("Segoe UI Emoji", font_size_max)
        )
        
        # Posicionar mensaje
        x_msg = avatar_margin if is_bot else SCROLL_AREA.width - msg_surface.get_width() - avatar_margin
        surfaces.append((msg_surface, x_msg, y_offset, msg_height))
        
        # Actualizar offset vertical para el siguiente mensaje
        y_offset += alto
    
    # --- Superficie de desplazamiento ---
    total_height = sum(alturas)
    
    # Verificar si tenemos una superficie en caché para este tamaño
    scroll_surface_key = "scroll_surface"
    scroll_surface = _surface_cache.get(scroll_surface_key)
    
    # Crear nueva superficie si es necesario
    if scroll_surface is None or scroll_surface.get_size() != (SCROLL_AREA.width, max(SCROLL_AREA.height, total_height)):
        scroll_surface = pygame.Surface(
            (SCROLL_AREA.width, max(SCROLL_AREA.height, total_height)), 
            pygame.SRCALPHA
        )
        _surface_cache.put(scroll_surface_key, scroll_surface)
    else:
        # Limpiar superficie existente
        scroll_surface.fill((0,0,0,0))
    
    # Dibujar todos los elementos en la superficie de desplazamiento
    for surface, x, y, _ in surfaces:
        scroll_surface.blit(surface, (x, y))
    
    # Blit del área visible a la pantalla
    pantalla.blit(
        scroll_surface, 
        (SCROLL_AREA.x, SCROLL_AREA.y), 
        area=pygame.Rect(0, 0, SCROLL_AREA.width, SCROLL_AREA.height)
    )
    
    # --- Barra de desplazamiento ---
    scroll_manager_local = globals().get('scroll_manager', None)
    if scroll_manager_local and hasattr(historial, 'get_total_height'):
        # Sincronizar scroll visual
        max_scroll = max(0, historial.get_total_height() - area_height)
        historial.set_scroll_offset_px(scroll_manager_local.update(max_scroll))
        scroll_pos = historial.scroll_offset_px
    else:
        scroll_pos = 0
        max_scroll = 0
    
    # Dibujar barra de desplazamiento
    dibujar_barra_scroll(
        pantalla,
        ANCHO - SCROLL_WIDTH - SCROLL_MARGIN,
        SCROLL_AREA.y,
        SCROLL_WIDTH,
        SCROLL_AREA.height,
        scroll_pos,
        total_height,
        SCROLL_AREA.height,
        color=(150, 180, 255),
        highlight=True,
        modern=True
    )
    
    return surfaces, total_height

def dibujar_entrada(pantalla):
    """
    Dibuja el campo de entrada de texto con adaptación a redimensionamiento.
    
    Args:
        pantalla: Superficie donde dibujar
    """
    # Obtener constantes visuales
    c = get_visual_constants()
    sx, sy = scaler.scale_x_value, scaler.scale_y_value
    
    # Calcular posición y dimensiones adaptativas
    is_small_screen = c["ANCHO"] < 450
    
    # Adaptar según tamaño de pantalla
    if is_small_screen:
        # Pantalla pequeña - campo de entrada más angosto
        x = sx(10)
        button_space = sx(140)  # Espacio para 3 botones en columna
    else:
        # Pantalla normal/grande
        x = sx(20)
        button_space = sx(160)  # Espacio para botones en fila
    
    # Posición vertical común
    y = c["ALTO"] - sy(55)
    
    # Calcular ancho adaptativo
    w = c["ANCHO"] - button_space - sx(40) - x
    h = max(35, sy(48))
    
    # Crear y dibujar caja de entrada
    rect = pygame.Rect(x, y, w, h)
    color_fill = (230, 230, 235) if state['esperando_respuesta'] else c["COLOR_ENTRADA"]
    
    # Dibujar fondo
    pygame.draw.rect(pantalla, color_fill, rect, border_radius=c["BORDER_RADIUS"])
    pygame.draw.rect(pantalla, (200, 200, 205), rect, 1, border_radius=c["BORDER_RADIUS"])
    
    # Renderizar y recortar texto si es necesario
    texto = state['entrada_usuario']
    font = c["FUENTE"]
    
    # Usar función optimizada para recortar texto
    texto_visible, _ = recortar_texto_eficiente(texto, font, rect.width - sx(24))
    
    if texto_visible:
        # Renderizar con centrado vertical
        text_surf = font.render(texto_visible, True, c["COLOR_TEXTO"])
        text_y = rect.y + (rect.height - text_surf.get_height()) // 2
        pantalla.blit(text_surf, (rect.x + sx(12), text_y))

def dibujar_botones(pantalla):
    """
    Dibuja los botones de la interfaz con adaptación a tema y estado.
    
    Args:
        pantalla: Superficie donde dibujar
    """
    botones = get_botones()
    
    for boton in botones:
        # Ocultar botón de voz si no hay respuesta del bot
        if boton.id == "voz" and not hay_respuesta_bot(historial):
            continue
        
        # Deshabilitar botones según estado
        if boton.id in ("enviar", "voz") and state['esperando_respuesta']:
            boton.color_normal = (180, 180, 180)
            boton.color_hover = (180, 180, 180)
        else:
            # Adaptar colores al tema actual
            theme_colors = _get_theme_constants(state['theme'])
            is_dark = theme_colors["COLOR_FONDO"][0] < 100
            
            if is_dark:
                # Tema oscuro
                boton.color_normal = (60, 60, 65)
                boton.color_hover = (80, 80, 85)
            else:
                # Tema claro
                boton.color_normal = (255, 255, 255)
                boton.color_hover = (230, 230, 235)
        
        # Dibujar botón
        boton.draw(pantalla)

def update_animations(dt):
    """
    Actualiza todas las animaciones del chatbot.
    
    Args:
        dt: Tiempo desde último frame en segundos
    """
    # Aquí se pueden implementar más animaciones en el futuro
    pass

# Exportar funciones y variables públicas
__all__ = [
    "dibujar_entrada",
    "dibujar_botones",
    "renderizar_historial",
    "update_animations",
    "state",
    "historial",
    "scroll_manager",
    "get_visual_constants",
    "set_render_area",
    "get_botones",
    "initialize_chatbot",
    "DEFAULT_WELCOME_MESSAGES",
    "set_theme",
    "THEMES"
]
