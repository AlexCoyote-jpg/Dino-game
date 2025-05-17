import pygame
import sys
from core.decoration.background_game import FondoAnimado
from core.scale.responsive_scaler_animated import ResponsiveScalerAnimado

def main():
    pygame.init()
    ANCHO, ALTO = 900, 700
    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
    pygame.display.set_caption("Prueba FondoAnimado")

    scaler = ResponsiveScalerAnimado(initial_width=1280, initial_height=720)
    fondo = FondoAnimado(pantalla)
    fondo.set_escaladores(scaler.sx, scaler.sy)
    fondo.resize(ANCHO, ALTO)

    clock = pygame.time.Clock()
    running = True
    frames = 0

    while running and frames < 6000:  # Corre la prueba por ~5 segundos a 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                ANCHO, ALTO = event.w, event.h
                pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
                scaler.update(ANCHO, ALTO)
                fondo.set_escaladores(scaler.sx, scaler.sy)
                fondo.resize(ANCHO, ALTO)

        scaler.tick()
        fondo.update()
        fondo.draw()

        pygame.display.flip()
        clock.tick(60)
        frames += 1

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
