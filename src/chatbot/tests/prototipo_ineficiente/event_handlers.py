import pygame
import sys
from chatbot.voz import hablar, detener
from chatbot.Conexion import obtener_respuesta_async
from chatbot.Configs import LLAMA

def hay_respuesta_bot(historial):
    # historial puede ser ChatbotStateManager o lista
    if hasattr(historial, 'all_messages'):
        return any(msg.startswith("Bot: ") for msg in historial.all_messages)
    return any(msg.startswith("Bot: ") for msg in historial)

def manejar_voz(historial):
    pygame.mixer.Sound("assets/sonidos/acierto.wav").play()
    mensajes = historial.all_messages if hasattr(historial, 'all_messages') else historial
    for msg in reversed(mensajes):
        if msg.startswith("Bot: "):
            hablar(msg[5:])
            break

def procesar_mensaje_async(state, historial, callback):
    mensaje = state['entrada_usuario'].strip()
    if mensaje and not state['esperando_respuesta']:
        state['esperando_respuesta'] = True
        if hasattr(historial, 'add_message'):
            historial.add_message(f"Tú: 🧑‍💬 {mensaje}")
        else:
            historial.append(f"Tú: 🧑‍💬 {mensaje}")
        state['entrada_usuario'] = ""
        obtener_respuesta_async(mensaje, LLAMA.model, LLAMA.api_key, callback=callback)

def respuesta_callback(respuesta, historial, state):
    if hasattr(historial, 'add_message'):
        historial.add_message(f"Bot: {respuesta}")
    else:
        historial.append(f"Bot: {respuesta}")
    state['esperando_respuesta'] = False

def handle_key_event(event, state, enviar_callback):
    if event.key == pygame.K_RETURN:
        enviar_callback()
    elif event.key == pygame.K_BACKSPACE:
        state['entrada_usuario'] = state['entrada_usuario'][:-1]
    elif event.unicode.isprintable():
        state['entrada_usuario'] += event.unicode

def manejar_click(pos, botones, state):
    detener()
    if state['esperando_respuesta']:
        return
    for boton in botones:
        if boton.collidepoint(pos):
            fake_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': pos, 'button': 1})
            boton.handle_event(fake_event)
            break

def handle_mouse_event(event, scroll_manager, max_scroll, area_y, area_height, bar_rect, botones, state):
    if event.type == pygame.MOUSEBUTTONDOWN:
        manejar_click(event.pos, botones, state)
    scroll_manager.handle_event(
        event,
        wheel_speed=40,
        thumb_rect=None,
        max_scroll=max_scroll,
        h=area_height,
        y=area_y,
        bar_rect=bar_rect
    )

def process_events(events, state, historial, scroll_manager, max_scroll, scroll_area, bar_rect, botones):
    for event in events:
        if event.type == pygame.QUIT:
            detener()
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            handle_key_event(
                event,
                state,
                lambda: procesar_mensaje_async(
                    state,
                    historial,
                    lambda r: respuesta_callback(r, historial, state)
                )
            )
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            handle_mouse_event(
                event,
                scroll_manager,
                max_scroll,
                scroll_area.y,
                scroll_area.height,
                bar_rect,
                botones,
                state
            )
        # Scroll con ChatbotStateManager
        if hasattr(historial, 'scroll_up'):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    historial.scroll_up()
                elif event.key == pygame.K_DOWN:
                    historial.scroll_down()
