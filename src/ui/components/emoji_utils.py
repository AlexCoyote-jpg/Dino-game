import pygame
from ui.components.emoji import get_emoji_renderer

def render_texto_emojis(texto, font_size=28, color=(0,0,0)):
    """
    Renderiza texto (con emojis, símbolos y saltos de línea) en una superficie ajustada al tamaño del contenido.
    Devuelve la superficie y el tamaño (ancho, alto).
    """
    renderer = get_emoji_renderer()
    # Divide el texto en líneas solo por saltos de línea reales
    lines = renderer.get_lines(texto, 9999, font_size)
    font = renderer.get_font(font_size)
    line_height = font.get_height()
    width = max(renderer.measure_text_width(line, font_size) for line in lines) if lines else 1
    height = len(lines) * line_height if lines else line_height
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for i, line in enumerate(lines):
        renderer.render_line(surface, line, 0, i * line_height, font_size, color)
    return surface, (width, height)
