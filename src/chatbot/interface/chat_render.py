import pygame
from ui.components.utils import dibujar_caja_texto
from ui.components.scroll import dibujar_barra_scroll
from ui.components.emoji import get_emoji_renderer

BUBBLE_PADDING = 14

def draw_burbuja(pantalla, font, chat_x, chat_w, linea, color, bg, ali, y):
    emoji_renderer = get_emoji_renderer()
    font_size = font.get_height()

    temp_surf = pygame.Surface((chat_w, font_size * 3), pygame.SRCALPHA)
    emoji_renderer.render_line(temp_surf, linea, 0, 0, font_size, color)
    text_rect = temp_surf.get_bounding_rect()

    line_height = text_rect.height
    vertical_padding = max(8, line_height // 4)
    bubble_rect = text_rect.inflate(BUBBLE_PADDING * 2, vertical_padding * 2)

    if ali == "der":
        bubble_rect.topright = (chat_x + chat_w - 10, y)
        text_rect.topright = (bubble_rect.topright[0] - BUBBLE_PADDING, bubble_rect.top + vertical_padding)
    else:
        bubble_rect.topleft = (chat_x + 10, y)
        text_rect.topleft = (bubble_rect.topleft[0] + BUBBLE_PADDING, bubble_rect.top + vertical_padding)

    pygame.draw.rect(pantalla, bg, bubble_rect, border_radius=12)
    emoji_renderer.render_line(pantalla, linea, text_rect.x, text_rect.y, font_size, color)

def render_chat(pantalla, chat_x, chat_y, chat_w, chat_h, font,
                _scroll_offset, _render_cache, _total_chat_height,
                _thumb_rect_ref, _mensajes_altos=None):

    dibujar_caja_texto(pantalla, chat_x, chat_y, chat_w, chat_h, (245, 245, 255, 220), radius=18)

    chat_clip_rect = pygame.Rect(chat_x, chat_y, chat_w - 20, chat_h + 8)
    pantalla.set_clip(chat_clip_rect)

    y = chat_y + 10 - _scroll_offset
    chat_bottom = chat_y + chat_h + 8
    use_cache = _mensajes_altos and len(_mensajes_altos) == len(_render_cache)
    draw_cb = getattr(render_chat, 'draw_burbuja_cb', None)

    if use_cache:
        for idx, (linea, color, bg, ali) in enumerate(_render_cache):
            line_height = _mensajes_altos[idx]
            if y + line_height <= chat_y:
                y += line_height
                continue
            if y >= chat_bottom:
                break
            if draw_cb:
                draw_cb(pantalla, linea, color, bg, ali, y)
            y += line_height
    else:
        line_height = font.get_linesize() + max(8, font.get_linesize() // 4) * 2
        for linea, color, bg, ali in _render_cache:
            if y + line_height <= chat_y:
                y += line_height
                continue
            if y >= chat_bottom:
                break
            if draw_cb:
                draw_cb(pantalla, linea, color, bg, ali, y)
            y += line_height

    pantalla.set_clip(None)

    if _total_chat_height > chat_h:
        barra_x, barra_y, barra_w, barra_h = chat_x + chat_w - 18, chat_y, 16, chat_h
        thumb_h = max(30, int(barra_h * (chat_h / _total_chat_height)))
        max_scroll = _total_chat_height - chat_h
        thumb_y = barra_y + int(_scroll_offset * (barra_h - thumb_h) / max_scroll) if max_scroll > 0 else barra_y

        _thumb_rect_ref[0] = pygame.Rect(barra_x, thumb_y, barra_w, thumb_h)
        dibujar_barra_scroll(pantalla, barra_x, barra_y, barra_w, barra_h,
                             _scroll_offset, _total_chat_height, chat_h,
                             color=(120, 180, 255), highlight=False, modern=True)
    else:
        _thumb_rect_ref[0] = None