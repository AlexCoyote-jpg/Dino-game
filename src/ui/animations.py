import pygame
import math

scaled_imgs_cache = {}  # Cache global para imágenes escaladas
hover_anim_states = {}  # Estado de hover por índice (0.0 a 1.0)

def get_scaled_image(img, size):
    if img is None:
        return None
    key = (id(img), size)
    if key not in scaled_imgs_cache:
        scaled_imgs_cache[key] = pygame.transform.smoothscale(img, (size, size))
    return scaled_imgs_cache[key]

def actualizar_hover_state(idx, is_hover, velocidad=0.15):
    """
    Actualiza el estado de hover (0.0 a 1.0) de forma más gradual para una animación más fluida.
    """
    state = hover_anim_states.get(idx, 0.0)
    state += velocidad if is_hover else -velocidad
    state = max(0.0, min(1.0, state))
    hover_anim_states[idx] = state
    return state

def get_surface(ancho, alto, alpha=False):
    flags = pygame.SRCALPHA if alpha else 0
    return pygame.Surface((ancho, alto), flags)

def elementos(caja, juego, recursos, cx, cy, tam_caja, fuente):
    img = recursos.get(juego["imagen"])
    if img:
        padding = 16
        img_w = img_h = tam_caja - 2 * padding
        img_scaled = get_scaled_image(img, img_w)
        img_x = cx + (tam_caja - img_w) // 2
        img_y = cy + padding
        caja.blit(img_scaled, (img_x, img_y))

    from ui.components.utils import mostrar_texto_adaptativo
    mostrar_texto_adaptativo(
        caja,
        juego["nombre"],
        cx + 4, cy + tam_caja - 36,
        tam_caja - 8, 32,
        fuente,
        (30, 30, 60),
        centrado=True
    )

def renderizar_celda(caja, juego, recursos, fuente, x, y, tam, color, radio):
    """
    Renderiza una celda (tarjeta) con estilo minimalista y Apple-like.
    Dibuja una caja redondeada con un sutil contorno y luego incorpora los elementos (imagen y texto)
    sobre ella.
    """
    from ui.components.utils import dibujar_caja_texto
    # Dibujar la tarjeta con bordes redondeados (fondo de la celda)
    dibujar_caja_texto(caja, x, y, tam, tam, color=color, radius=radio)
    # Añadir un borde sutil para dar mayor definición al contorno de la tarjeta
    pygame.draw.rect(caja, (220, 220, 220), pygame.Rect(x, y, tam, tam), width=1, border_radius=radio)
    # Renderizar el contenido de la tarjeta (imagen y nombre)
    elementos(caja, juego, recursos, x, y, tam, fuente)

def animar_dinos(pantalla, imagenes_dinos, posiciones, escala, tiempo_ms, velocidad=1.0):
    """Versión mejorada con más parámetros de control y animaciones más suaves."""
    for i, (img_key, pos) in enumerate(zip(imagenes_dinos, posiciones)):
        # Parámetros de animación personalizados por dino
        fase = (tiempo_ms + i * 1000) / 500
        fase_escala = (tiempo_ms + i * 1000) / 800
        
        # Movimiento vertical más suave con easing
        t = abs(math.sin(fase * velocidad))
        t = t * t * (3 - 2 * t)  # Función de easing
        offset_y = int(10 * escala * t)
        
        # Escala con rebote suave
        t_escala = abs(math.sin(fase_escala * velocidad))
        t_escala = t_escala * t_escala * (3 - 2 * t_escala)
        escala_dino = escala * (1.0 + 0.1 * t_escala)
        
        # Calcular tamaños y posiciones
        tamaño_base = int(100 * escala)
        tamaño = int(100 * escala_dino)
        
        # Obtener imagen
        img = img_key  # Ahora img_key es directamente el objeto de imagen
        
        # Obtener imagen escalada
        img_scaled = get_scaled_image(img, tamaño)
        
        if img_scaled:
            # Calcular posición con centrado
            pos_x = pos[0] - (tamaño - tamaño_base) // 2
            pos_y = pos[1] - offset_y - (tamaño - tamaño_base) // 2
            
            # Añadir sombra debajo del dino
            sombra_size = int(tamaño * 0.8)
            sombra = get_surface(sombra_size, sombra_size // 3, alpha=True)
            pygame.draw.ellipse(sombra, (0, 0, 0, 80 - int(40 * t)), sombra.get_rect())
            sombra_x = pos_x + (tamaño - sombra_size) // 2
            sombra_y = pos[1] + tamaño_base - sombra_size // 3
            pantalla.blit(sombra, (sombra_x, sombra_y))
            
            # Dibujar el dino
            pantalla.blit(img_scaled, (pos_x, pos_y))

def dibujar_caja_juegos(surface, x, y, w, h, juegos, recursos,
                         color=(248, 248, 248), alpha=0, radius=20,
                         margen=16, tam_caja_default=120, fuente=None, on_hover=None,
                         num_cols=3, num_rows=2):
    """
    Dibuja una caja con una cuadrícula de juegos al estilo Apple, con bordes 
    redondeados, sombras sutiles y un efecto de hover minimalista.
    
    Parámetros:
        surface: Superficie destino donde se dibuja la caja.
        x, y: Coordenadas de la esquina superior izquierda de la caja.
        w, h: Ancho y alto de la caja.
        juegos: Lista de juegos (diccionarios) a mostrar.
        recursos: Diccionario de recursos (por ejemplo, imágenes).
        color: Color de fondo (muy claro para estilo Apple).
        alpha: Transparencia del fondo (0 = opaco).
        radius: Radio de las esquinas (redondeado).
        margen: Espacio entre celdas.
        tam_caja_default: Tamaño de celda por defecto (se recalcula).
        fuente: Fuente para el texto; si es None se asigna una por defecto.
        on_hover: Callback al hacer hover (índice, rectángulo absoluto).
        num_cols: Número máximo de columnas.
        num_rows: Número máximo de filas.
        
    Retorna:
        Lista de rectángulos absolutos que definen las celdas dibujadas.
    """
    # Crear la superficie de la "caja" con soporte alpha si se indica
    caja = get_surface(w, h, alpha=alpha > 0)
    caja.fill((*color, alpha) if alpha > 0 else color)
    pygame.draw.rect(caja, (220, 220, 220), caja.get_rect(), width=1, border_radius=radius)
    
    # Calcular dimensiones de celda
    cell_width = (w - (num_cols + 1) * margen) // num_cols
    cell_height = (h - (num_rows + 1) * margen) // num_rows
    cell_size = min(cell_width, cell_height)
    
    # Determinar cantidad de celdas a dibujar y centrar la cuadrícula
    cols = min(num_cols, len(juegos))
    rows = min(num_rows, -(-len(juegos) // cols))  # ceil division
    max_juegos = min(cols * rows, len(juegos))
    
    total_grid_width = cols * cell_size + (cols - 1) * margen
    total_grid_height = rows * cell_size + (rows - 1) * margen
    offset_x = (w - total_grid_width) // 2
    offset_y = (h - total_grid_height) // 2
    
    if fuente is None:
        fuente = pygame.font.SysFont("San Francisco", 22, bold=True)
    
    rects = []
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    for idx in range(max_juegos):
        col = idx % cols
        row = idx // cols
        local_x = offset_x + col * (cell_size + margen)
        local_y = offset_y + row * (cell_size + margen)
        abs_rect = pygame.Rect(x + local_x, y + local_y, cell_size, cell_size)
        rects.append(abs_rect)
    
        # Dibujar sombra sutil para profundidad
        shadow = get_surface(cell_size, cell_size, alpha=True)
        pygame.draw.rect(shadow, (0, 0, 0, 30), shadow.get_rect(), border_radius=radius-4)
        caja.blit(shadow, (local_x + 2, local_y + 2))
    
        is_hover = abs_rect.collidepoint(mouse_x, mouse_y)
        hover_state = actualizar_hover_state(idx, is_hover)
    
        if hover_state > 0:
            scale = 1.0 + 0.1 * hover_state
            render_size = int(cell_size * scale)
            render_x = local_x - (render_size - cell_size) // 2
            render_y = local_y - (render_size - cell_size) // 2
            br = radius if hover_state > 0.9 else radius - 4
            renderizar_celda(caja, juegos[idx], recursos, fuente, render_x, render_y, render_size, (200, 230, 255), br)
            if is_hover and on_hover:
                on_hover(idx, abs_rect)
        else:
            renderizar_celda(caja, juegos[idx], recursos, fuente, local_x, local_y, cell_size, (180, 200, 230), radius-4)
    
    surface.blit(caja, (x, y))
    return rects
