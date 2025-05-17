import pygame
from chatbot.prototipo_ineficiente.chatbot import ChatBotScreen

ANCHO_INICIAL, ALTO_INICIAL = 800, 600

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_INICIAL, ALTO_INICIAL), pygame.RESIZABLE)
    pygame.display.set_caption("Test ChatBotScreen en área redimensionable")
    clock = pygame.time.Clock()

    def calcular_area_chatbot(w, h):
        ancho = int(w * 0.75)
        alto = int(h * 0.75)
        x = (w - ancho) // 2
        y = (h - alto) // 2
        return pygame.Rect(x, y, ancho, alto)

    area_chatbot = calcular_area_chatbot(ANCHO_INICIAL, ALTO_INICIAL)
    chatbot_screen = ChatBotScreen(None, area_chatbot)

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                pantalla = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                area_chatbot = calcular_area_chatbot(event.w, event.h)
                chatbot_screen.area = area_chatbot
                if hasattr(chatbot_screen, "resize"):
                    chatbot_screen.resize(event.w, event.h)

        pantalla.fill((30, 30, 30))
        chatbot_screen.handle_events(events)
        chatbot_screen.update(clock.get_time())
        chatbot_screen.draw(pantalla)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()