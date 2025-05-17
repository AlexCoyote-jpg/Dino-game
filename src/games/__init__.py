# Permite que la carpeta sea reconocida como un módulo de Python
# En __init__:
# Permite que la carpeta sea reconocida como un módulo de Python

from .dino_suma_resta import JuegoSumaResta
from .memoria_jurasica import JuegoMemoriaJurasica
from .dino_cazador import JuegoCazadorNumeros
from .rescate_jurasico import JuegoRescate
from .Dino_Logico import JuegoLogico
from .mi_juego import MiJuego
# from .otro_juego import OtroJuego  # Descomenta y agrega más juegos aquí

# Lista centralizada de juegos (opcional, para usar en el menú principal)
JUEGOS_DISPONIBLES = [
    {"nombre": "Dino Sumas/Resta", "clase": JuegoSumaResta, "imagen": "dino1"},
    {"nombre": "Dino Cazador", "clase": JuegoCazadorNumeros, "imagen": "dino2"},
    {"nombre": "Dino Logico", "clase": JuegoLogico, "imagen": "dino3"},
    {"nombre": "Memoria Jurasica", "clase": JuegoMemoriaJurasica, "imagen": "dino4"},
    {"nombre": "Mi Juego", "clase": MiJuego, "imagen": "dino5"},
    {"nombre": "Rescate Jurásico", "clase": JuegoRescate, "imagen": "dino5"},
    # {"nombre": "Otro Juego", "func": OtroJuego},
]

# Ejemplo de cómo podrías usarlo en el menú principal
#from games import JUEGOS_DISPONIBLES

# Luego en tu clase MenuPrincipal:
#self.juegos = JUEGOS_DISPONIBLES

# ejemplo de cómo podrías usarlo en el menú principal 2
'''
self.juegos = [
    {"nombre": "Juego de Sumas", "rect": pygame.Rect(...), "func": juego_sumas},
    # {"nombre": "Otro Juego", "rect": pygame.Rect(...), "func": otro_juego},
]
# En mostrar_juegos:
for juego in self.juegos:
    dibujar_caja_texto(self.pantalla, *juego["rect"], (180, 220, 255))
    mostrar_texto_adaptativo(self.pantalla, juego["nombre"], *juego["rect"], self.font_texto, (30,30,30), centrado=True)
# En run:
if event.type == pygame.MOUSEBUTTONDOWN:
    for juego in self.juegos:
        if juego["rect"].collidepoint(event.pos):
            juego["func"](self.pantalla, self.config)
'''