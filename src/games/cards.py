"""
Funciones para dibujar cartas genéricas del juego de memoria.
"""
import pygame
from ui.components.utils import dibujar_caja_texto, mostrar_texto_adaptativo

def dibujar_carta_generica(
    pantalla, carta, x, y, ancho, alto, fuente, color_texto, color_acierto, color_error, color_borde, img_reverso, color_borde_reverso
):
    escala = 1.0 + carta.get('animacion', 0.0) * 0.1
    ancho_real = int(ancho * escala)
    alto_real = int(alto * escala)
    x_offset = (ancho_real - ancho) // 2
    y_offset = (alto_real - alto) // 2
    rect = pygame.Rect(x - x_offset, y - y_offset, ancho_real, alto_real)
    if carta.get('id') in carta.get('cartas_emparejadas', set()) or carta.get('volteada', False):
        color_fondo = (60, 60, 100) if carta.get('tipo') == 'operacion' else (100, 60, 60)
        dibujar_caja_texto(pantalla, rect.x, rect.y, rect.width, rect.height, color_fondo, radius=10)
        mostrar_texto_adaptativo(
            pantalla, carta.get('valor', ''), rect.x, rect.y, rect.width, rect.height, fuente, color_texto, centrado=True
        )
        if carta.get('bordes') == 'acierto':
            pygame.draw.rect(pantalla, color_acierto, rect, 4, border_radius=10)
        elif carta.get('bordes') == 'error':
            pygame.draw.rect(pantalla, color_error, rect, 4, border_radius=10)
        else:
            pygame.draw.rect(pantalla, color_borde, rect, 3, border_radius=10)
    else:
        img = pygame.transform.scale(img_reverso, (ancho_real, alto_real))
        pantalla.blit(img, rect)
        pygame.draw.rect(pantalla, color_borde_reverso, rect, 2, border_radius=10)
    return rect
