import sys
import pygame

# importa tu screen_manager y la clase MiJuego
from ui.screen_manager import (
    create_screen_manager,
    set_screen,
    handle_event_screen,
    update_screen,
    draw_screen,
    HomeScreen
)
from games.mi_juego import MiJuego
from core.decoration.background import FondoAnimado
from ui.navigation_bar import NavigationBar
from games import JUEGOS_DISPONIBLES

def run():
    pygame.init()
    ANCHO, ALTO = 900, 700
    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
    pygame.display.set_caption("Mi Juego Principal")

    # — Recursos compartidos —
    fondo    = FondoAnimado(ANCHO, ALTO)
    navbar   = NavigationBar(["Home","MiJuego"])
    images   = {}   # tu diccionario de imágenes
    sounds   = {}   # tu diccionario de sonidos
    config   = {}   # tu config
    screen_manager = create_screen_manager()

    # — Pantalla Home como estado inicial —
    class HomeDummy:
        def __init__(self): pass
        def handle_event(self, e):
            # al presionar botón o tecla, lanzamos MiJuego
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                # instanciamos MiJuego pasándole return_to_menu
                def volver(): set_screen(screen_manager, HomeDummy())
                instancia = MiJuego(
                    pantalla, config, "Normal",
                    fondo, navbar, images, sounds,
                    return_to_menu=volver
                )
                set_screen(screen_manager, instancia)
        def update(self, dt): pass
        def draw(self, surf):
            surf.fill((30,30,30))
            font = pygame.font.SysFont(None,36)
            txt = font.render("HOME – presiona SPACE para MiJuego", True, (200,200,200))
            surf.blit(txt, txt.get_rect(center=surf.get_rect().center))

    # Inicializamos con HomeDummy
    set_screen(screen_manager, HomeDummy())

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # 1) Capturar eventos
        eventos = pygame.event.get()
        for e in eventos:
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.VIDEORESIZE:
                ANCHO, ALTO = e.w, e.h
                pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
                fondo.resize(ANCHO, ALTO)

            # 2) Procesar navbar si quieres usarla
            sel = navbar.handle_event(e)
            # ... aquí cambiar pantallas según sel si lo deseas

        # 3) Delegar todos los eventos al screen activo (incluye MiJuego)
        handle_event_screen(screen_manager, eventos)

        # 4) Actualizar fondo y screen activo
        fondo.update(dt * 60)
        update_screen(screen_manager, dt)

        # 5) Dibujar
        fondo.draw(pantalla)
        draw_screen(screen_manager, pantalla)
        navbar.draw(pantalla, None)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run()
