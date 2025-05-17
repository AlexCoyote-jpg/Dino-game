import pygame

# Este archivo está pensado para contener el "estado global" del juego.
# Por ejemplo: usuario actual, progreso, configuración, puntuaciones, etc.
# Así puedes compartir información entre pantallas o juegos.

# Ejemplo de estructura básica:
class GameState:
    def __init__(self):
        self.usuario = None
        self.puntuaciones = {}
        self.configuracion = {}
        self.progreso = {}

# Puedes crear una instancia global si lo necesitas:
game_state = GameState()
