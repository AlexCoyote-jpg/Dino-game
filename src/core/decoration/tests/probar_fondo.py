import pygame
from core.decoration.background import FondoAnimado

ANCHO, ALTO = 800, 600

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
pygame.display.set_caption('Prueba de FondoAnimado')
clock = pygame.time.Clock()

# Usar la nueva clase eficiente
fondo = FondoAnimado(ANCHO, ALTO)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            ANCHO, ALTO = event.w, event.h
            pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
            fondo.resize(ANCHO, ALTO)

    fondo.update()
    fondo.draw(pantalla)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
