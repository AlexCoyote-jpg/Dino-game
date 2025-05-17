import pygame
from utils_antiguo import Boton, Boton_Images

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((600, 300))
    pygame.display.set_caption("Prueba de Botones")

    # Cargar imagen de ejemplo
    try:
        img_encendido = pygame.image.load("assets/imagenes/encendido.png").convert_alpha()
        img_encendido = pygame.transform.smoothscale(img_encendido, (32, 32))
    except Exception as e:
        print("No se pudo cargar la imagen:", e)
        img_encendido = None

    # Crear botones de diferentes estilos
    botones = [
        Boton("Apple", 50, 50, 150, 60, estilo="apple", border_color=(255,0,0), border_width=4, color_hover=(200, 220, 255)),
        Boton("Flat", 250, 50, 150, 60, estilo="flat", color_hover=(200, 220, 255)),
        Boton("Round", 450, 50, 60, 60, estilo="round", color_hover=(255, 200, 200)), 
        # Botón con imagen a la izquierda
        Boton_Images(
            "Con Imagen", 50, 150, 180, 60,
            imagen=img_encendido, imagen_pos="top",
            color_hover=(210, 255, 210)
        ),
        # Botón round con imagen centrada
        Boton_Images(
            "", 300, 150, 60, 60,
            imagen=img_encendido,border_color=(255,0,0), border_width=4 ,imagen_pos="center",
            estilo="round", color_hover=(255, 255, 200)
        ),
        
    ]

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                for boton in botones:
                    if boton.collidepoint(evento.pos):
                        print(f"Botón '{getattr(boton, 'texto', '')}' presionado")

        pantalla.fill((240, 240, 240))
        for boton in botones:
            boton.draw(pantalla)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()