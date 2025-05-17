from .chat_utils import wrap_text

def calcular_offset_ultimo_usuario(historial, font, chat_w, total_chat_height, chat_h):
    offset = 0
    ancho_texto = chat_w - 40
    line_height = font.get_linesize() + max(8, int(font.get_linesize() * 0.25)) * 2
    ultimo_usuario_offset = 0
    for autor, texto in historial:
        lineas = wrap_text(texto, font, ancho_texto)
        if autor == "usuario":
            ultimo_usuario_offset = offset
        offset += line_height * len(lineas)
    max_scroll = max(0, total_chat_height - chat_h)
    return min(ultimo_usuario_offset, max_scroll)
