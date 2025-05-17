"""
Gestor funcional de pantallas: maneja el cambio y la gestión de diferentes pantallas o vistas del juego.
"""

class ScreenManager:
    def __init__(self):
        self.current_screen = None

    def set_screen(self, screen):
        self.current_screen = screen

    def get_screen(self):
        return self.current_screen

    def handle_event(self, eventos):
        if self.current_screen and hasattr(self.current_screen, "handle_event"):
            if isinstance(eventos, list):
                for event in eventos:
                    self.current_screen.handle_event(event)
            else:
                self.current_screen.handle_event(eventos)

    def update(self, dt=None):
        if self.current_screen and hasattr(self.current_screen, "update"):
            try:
                if dt is not None:
                    self.current_screen.update(dt)
                else:
                    self.current_screen.update()
            except TypeError:
                self.current_screen.update()

    def draw(self, surface):
        if self.current_screen and hasattr(self.current_screen, "draw"):
            self.current_screen.draw(surface)

class GameScreen:
    def handle_event(self, eventos):
        pass

    def update(self, dt=None):
        pass

    def draw(self, surface):
        pass

class HomeScreen(GameScreen):
    def __init__(self, menu):
        self.menu = menu

    def draw(self, surface):
        self.menu.mostrar_home()

class JuegosScreen(GameScreen):
    def __init__(self, menu, dificultad):
        self.menu = menu
        self.dificultad = dificultad

    def handle_event(self, eventos):
        if hasattr(self.menu, "handle_juegos_eventos"):
            self.menu.handle_juegos_eventos(eventos)

    def draw(self, surface):
        self.menu.mostrar_juegos(self.dificultad)

class ChatBotScreen(GameScreen):
    def __init__(self, menu):
        self.menu = menu

    def handle_event(self, eventos):
        if hasattr(self.menu, "handle_chatbot_eventos"):
            self.menu.handle_chatbot_eventos(eventos)

    def draw(self, surface):
        self.menu.mostrar_chatbot()

class GameInstanceScreen(GameScreen):
    def __init__(self, game_instance):
        self.game_instance = game_instance

    def handle_event(self, eventos):
        if hasattr(self.game_instance, "handle_event"):
            self.game_instance.handle_event(eventos)

    def update(self, dt=None):
        if hasattr(self.game_instance, "update"):
            self.game_instance.update(dt)

    def draw(self, surface):
        if hasattr(self.game_instance, "draw"):
            self.game_instance.draw(surface)

# Agrega estas funciones utilitarias al final del archivo para compatibilidad con el resto del proyecto
#callback
def set_screen(screen_manager, screen):
    """Set the current active screen."""
    screen_manager.set_screen(screen)
    return screen_manager

def handle_event_screen(screen_manager, eventos):
    """Delegate events to the current screen."""
    screen_manager.handle_event(eventos)

def update_screen(screen_manager, dt=None):
    """Update the current screen."""
    screen_manager.update(dt)

def draw_screen(screen_manager, surface):
    """Draw the current screen."""
    screen_manager.draw(surface)
    
