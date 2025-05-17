import pygame
import sys
import random
from core.decoration.effects import EffectsMixin

class DummyGame(EffectsMixin):
    def __init__(self, pantalla, ancho, alto):
        self.pantalla = pantalla
        self.ANCHO = ancho
        self.ALTO = alto
        self.navbar_height = 0
        self.sx = lambda x: x
        self.sy = lambda y: y
        self.fuente = pygame.font.SysFont(None, 36)
        self.racha_correctas = 0
        self.mejor_racha = 0
        self.tiempo_cambio_racha = 0
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.mensaje_color = (255, 255, 255, 220)
        self.mensaje_animacion = 1.0
        self.sonido_activado = False
        self.sounds = {}
        self.estrellas = []
        self.particulas = []

    def update(self):
        self.update_animacion_estrellas()
        self.update_animacion_estrellas_simple()
        self.update_particulas()
        if random.random() < 0.01:
            self.crear_efecto_estrellas((random.randint(100, self.ANCHO-100), random.randint(100, self.ALTO-100)))
        if random.random() < 0.01:
            self.crear_efecto_estrellas_simple((random.randint(100, self.ANCHO-100), random.randint(100, self.ALTO-100)))
        if random.random() < 0.01:
            self.crear_explosion_particulas(random.randint(100, self.ANCHO-100), random.randint(100, self.ALTO-100))

    def draw(self):
        self.pantalla.fill((30, 30, 40))
        self.draw_animacion_estrellas()
        self.draw_animacion_estrellas_simple()
        self.draw_particulas()
        self.dibujar_feedback()

def main():
    pygame.init()
    ANCHO, ALTO = 900, 700
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Prueba EffectsMixin (feedback, estrellas y partículas)")

    juego = DummyGame(pantalla, ANCHO, ALTO)
    clock = pygame.time.Clock()
    running = True

    # Mostrar feedback de prueba al inicio
    juego.mostrar_feedback(True)
    juego.mostrar_feedback(False, respuesta_correcta="42")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        juego.update()
        juego.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()