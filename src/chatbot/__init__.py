
'''
import pygame
from game.resources import Recursos
from game.menu import MenuPrincipal
from game.background import FondoAnimadoThread
from game.game import Game

def main():
    pygame.init()
    screen_width, screen_height = Recursos.ANCHO, Recursos.ALTO
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Jugando con Dino")

    Recursos.cargar_imagenes()
    Recursos.cargar_sonidos()

    game = Game(screen)
    game.run()

    pygame.quit()

if __name__ == "__main__":
    main()
'''