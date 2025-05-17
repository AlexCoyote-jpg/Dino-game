import pygame
import math
scaled_imgs_cache = {}
def get_scaled_image(img, size):
    if img is None:
        return None
    key = (id(img), size)
    if key not in scaled_imgs_cache:
        scaled_imgs_cache[key] = pygame.transform.smoothscale(img, (size, size))
    return scaled_imgs_cache[key]

def get_surface(ancho, alto, alpha=False):
    flags = pygame.SRCALPHA if alpha else 0
    return pygame.Surface((ancho, alto), flags)
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