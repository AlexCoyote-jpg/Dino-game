import pygame
from chatbot.chatbot_state import ChatbotStateManager
from ui.components.emoji import mostrar_alternativo_adaptativo

# Inicializar Pygame y pantalla
pygame.init()
pantalla = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Test ChatbotStateManager")

# Estado: mostrar solo últimos 5 o todos los mensajes
mostrar_todos = False

# Crear el gestor de estados con un máximo de 5 mensajes para modo compacto
state = ChatbotStateManager(max_visible=5)

# Mensajes de prueba iniciales
mensajes_prueba = [
    "¡Hola! 😊",
    "¿Cómo estás?",
    "Este es un mensaje de prueba.",
    "¡Pygame y emojis funcionando! 🦖",
    "Prueba de gestor de estados.",
    "¡Puedes agregar más mensajes!",
    "Soporta varios emojis: 😂❤️👍",
    "Texto largo para ver el ajuste automático.",
    "¡Último mensaje visible!",
    "¿Qué tal el chatbot?",
    "Este mensaje debería desplazar el primero.",
    "¡Funciona bien!",
    "¿Quieres probar más emojis? 😁🎉"
    "¿Listo para el siguiente nivel?",
    "¡Vamos a jugar! 🎮",
    "¿Qué tal un juego de matemáticas?",
    "¡Espero que te diviertas!",
    "¡Hasta luego! 👋",
    "¡Nos vemos pronto! €£¥",
    "¿Tienes alguna pregunta?+, -, =, ×, ÷, <, >, ≤, ≥, =. ",
]

# Agregar mensajes de prueba al estado
for msg in mensajes_prueba:
    state.add_message(msg)

clock = pygame.time.Clock()
running = True
input_mode = False
nuevo_mensaje = ""
font = pygame.font.SysFont("Segoe UI", 24)

'''
Controles:
- ENTER: Escribir mensaje nuevo
- ESC: Cancelar entrada de texto
- BACKSPACE: Borrar carácter en entrada
- C: Limpiar mensajes
- A: Mensaje largo de prueba
- Q: Salir
- 1: Solo últimos 5 mensajes (sin scroll)
- 2: Mostrar todos los mensajes (con scroll y paginado)
- ↑/↓: Scroll (solo en modo "todos")
'''

# Configuración de área de mensajes
mensaje_area_x = 40
mensaje_area_y = 40
mensaje_area_w = 700
mensaje_area_h = 450  # Reservar espacio para instrucciones y entrada

mensaje_alto = 40
mensaje_espacio = 5
mensajes_por_pagina = mensaje_area_h // (mensaje_alto + mensaje_espacio)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Entrada de texto para agregar mensajes nuevos
        if input_mode:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if nuevo_mensaje.strip():
                        state.add_message(nuevo_mensaje)
                    nuevo_mensaje = ""
                    input_mode = False
                elif event.key == pygame.K_ESCAPE:
                    nuevo_mensaje = ""
                    input_mode = False
                elif event.key == pygame.K_BACKSPACE:
                    nuevo_mensaje = nuevo_mensaje[:-1]
                else:
                    nuevo_mensaje += event.unicode
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_mode = True
                elif event.key == pygame.K_c:
                    state.clear()
                elif event.key == pygame.K_a:
                    state.add_message("Mensaje largo de prueba: 😁❤️💕😀 " * 10)
                elif event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_1:
                    # Solo mostrar los últimos 5 mensajes, sin scroll
                    mostrar_todos = False
                    state.max_visible = 5
                    state.visible_start = max(0, len(state.all_messages) - state.max_visible)
                    state.needs_redraw = True
                elif event.key == pygame.K_2:
                    # Mostrar todos los mensajes, scroll habilitado y paginado
                    mostrar_todos = True
                    state.max_visible = mensajes_por_pagina
                    state.visible_start = max(0, len(state.all_messages) - state.max_visible)
                    state.needs_redraw = True
                elif event.key == pygame.K_UP and mostrar_todos:
                    state.scroll_up()
                elif event.key == pygame.K_DOWN and mostrar_todos:
                    state.scroll_down()

    # Redibuja si hay cambios o en modo de entrada
    if state.should_redraw() or input_mode:
        pantalla.fill((245, 245, 245))

        # Dibuja el área de mensajes
        pygame.draw.rect(pantalla, (220, 220, 220), (mensaje_area_x-5, mensaje_area_y-5, mensaje_area_w+10, mensaje_area_h+10), border_radius=10)

        # Mostrar los mensajes actuales en el área definida
        y = mensaje_area_y
        for msg in state.get_messages():
            mostrar_alternativo_adaptativo(
                pantalla, msg, mensaje_area_x, y, mensaje_area_w, mensaje_alto, color=(0, 0, 0), centrado=False
            )
            y += mensaje_alto + mensaje_espacio

        # Si está en modo de entrada, muestra la caja de texto
        if input_mode:
            pygame.draw.rect(pantalla, (220, 220, 255), (mensaje_area_x, y, mensaje_area_w, mensaje_alto), border_radius=8)
            texto_render = font.render("Nuevo mensaje: " + nuevo_mensaje, True, (0, 0, 120))
            pantalla.blit(texto_render, (mensaje_area_x + 10, y + 8))
        else:
            instrucciones = [
                "ENTER: Escribir mensaje | C: Limpiar | A: Mensaje largo | Q: Salir",
                "1: Solo últimos 5 mensajes | 2: Mostrar todos | ↑/↓: Scroll (modo todos)",
                f"Modo actual: {'Todos los mensajes' if mostrar_todos else 'Solo últimos 5 mensajes'}"
            ]
            for idx, txt in enumerate(instrucciones):
                texto_render = font.render(txt, True, (80, 80, 80))
                pantalla.blit(texto_render, (mensaje_area_x, 510 + idx * 28))

        pygame.display.flip()
        state.mark_drawn()

    clock.tick(30)

pygame.quit()

'''
Mejoras menores posibles (opcional):
Si tienes muchísimos mensajes, podrías usar una estructura tipo deque para la lista interna, pero para la mayoría de los casos de uso de chatbots, una lista es suficiente.
Si quieres máxima eficiencia, asegúrate de que las fuentes y emojis se cargan/cachan solo una vez y no en cada frame (parece que ya lo haces).
Si el área de mensajes es muy grande y tienes animaciones, podrías usar un "dirty rects" para actualizar solo la zona de mensajes, pero para la mayoría de los chatbots esto no es necesario.
'''