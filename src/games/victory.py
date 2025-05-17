"""
Pantalla de victoria y botón para avanzar de nivel.
"""
import pygame
from ui.components.utils import mostrar_texto_adaptativo, Boton
from ui.components.emoji import mostrar_alternativo_adaptativo

def mostrar_victoria(
    pantalla, sx, sy, ancho, alto, fuente_titulo, fuente_texto, juego_base, carta_rects,
    color_panel=(255, 255, 224), color_borde=(255, 215, 0)
):
    ancho_panel = sx(500)
    alto_panel = sy(200)
    x_panel = (ancho - ancho_panel) // 2
    y_panel = (alto - alto_panel) // 2
    panel = pygame.Surface((ancho_panel, alto_panel), pygame.SRCALPHA)
    for i in range(alto_panel):
        factor = i / alto_panel
        r = int(255 - factor * 50)
        g = int(250 - factor * 20)
        b = int(150 + factor * 50)
        pygame.draw.line(panel, (r, g, b, 240), (0, i), (ancho_panel, i))
    pantalla.blit(panel, (x_panel, y_panel))
    pygame.draw.rect(pantalla, color_borde, (x_panel, y_panel, ancho_panel, alto_panel), 4, border_radius=20)
    mostrar_alternativo_adaptativo(
        pantalla, "¡FELICIDADES! 🎉",
        x_panel, y_panel + sy(20), ancho_panel, sy(60),
        fuente_titulo, (100, 160, 220), centrado=True
    )
    mostrar_texto_adaptativo(
        pantalla, "¡Has completado el memorama!",
        x_panel, y_panel + sy(80), ancho_panel, sy(40),
        fuente_texto, (30, 30, 30), centrado=True
    )
    # Usar la clase Boton en vez de dibujar_boton
    boton = Boton(
        "¡Reiniciar! 🔄",
        x_panel + (ancho_panel - sx(300)) // 2,
        y_panel + sy(130),
        sx(300), sy(50),
        color_normal=(100, 160, 220),
        color_hover=(30, 60, 120),
        fuente= pygame.font.SysFont("Segoe Emoji", 28),
        texto_adaptativo=True  # Esto permite que el botón use mostrar_texto_adaptativo, pero NO garantiza emojis.
    )
    boton.draw(pantalla)
    carta_rects.append((boton.rect, {'id': 'siguiente'}))
