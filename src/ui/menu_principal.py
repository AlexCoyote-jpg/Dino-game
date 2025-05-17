import pygame
import random
from ui.navigation_bar import NavigationBar
from ui.animations import animar_dinos, dibujar_caja_juegos
from ui.components.utils import Boton, dibujar_caja_texto, mostrar_texto_adaptativo, TooltipManager
from ui.components.emoji import mostrar_alternativo_adaptativo
from core.game_state import *
from games import JUEGOS_DISPONIBLES
from ui.screen_manager import (
    ScreenManager, HomeScreen, JuegosScreen, ChatBotScreen, GameInstanceScreen,
    set_screen, handle_event_screen, update_screen, draw_screen
)
from chatbot.interface.chatui import BotScreen
class MenuPrincipal:
    def __init__(self, pantalla, fondo, images, sounds, config, screen_manager=None):
        self.pantalla = pantalla
        self.base_width = pantalla.get_width()
        self.base_height = pantalla.get_height()

        self.fondo = fondo
        self.images = images
        self.sounds = sounds
        self.config = config

        self.niveles = ["Home", "Fácil", "Normal", "Difícil", "ChatBot"]
        tooltips = ["Ir al inicio", "Nivel básico", "Nivel intermedio", "Nivel difícil", "Habla con Dino"]
        self.navbar = NavigationBar(self.niveles, down=False, tooltips=tooltips)
        self.logo = self.images.get("dino_logo") if self.images else None

        self.imagenes_dinos = [self.images.get(f"dino{i+1}") for i in range(5)] if self.images else []
        self.dinos_actuales = [0, 1, 2]
        self.ultimo_cambio_dinos = pygame.time.get_ticks()

        self.clock = pygame.time.Clock()
        self.tooltip_manager = TooltipManager()

        self.fonts = {}
        self._precache_fonts()

        self.screen_manager = screen_manager or ScreenManager()

    def sx(self, x): return int(x * self.pantalla.get_width() / self.base_width)
    def sy(self, y): return int(y * self.pantalla.get_height() / self.base_height)

    def _precache_fonts(self):
        esc = self.pantalla.get_width() / 900
        self.fonts["titulo"] = pygame.font.SysFont("Segoe UI", int(54 * esc))
        self.fonts["texto"] = pygame.font.SysFont("Segoe UI", int(28 * esc))

    def mostrar_home(self):
        esc = min(self.pantalla.get_width() / 900, self.pantalla.get_height() / 700)
        x_t, y_t, w_t, h_t = (self.pantalla.get_width() - int(640 * esc)) // 2, int(110 * esc), int(640 * esc), int(60 * esc)
        dibujar_caja_texto(self.pantalla, x_t, y_t, w_t, h_t, (70, 130, 180))

        mostrar_texto_adaptativo(self.pantalla, "¡Bienvenido a Jugando con Dino!", x_t, y_t, w_t, h_t,
                                 self.fonts["titulo"], (255, 255, 255), centrado=True)

        # Caja instrucciones
        x_c, y_c, w_c, h_c = (self.pantalla.get_width() - int(600 * esc)) // 2, int(180 * esc), int(600 * esc), int(320 * esc)
        dibujar_caja_texto(self.pantalla, x_c, y_c, w_c, h_c, (255, 255, 255, 220))

        instrucciones = (
            "📚 ¡Aprende matemáticas jugando con Dino y sus amigos!\n\n"
            "🌱 Fácil: Juegos para principiantes\n"
            "🌻 Normal: Para quienes ya conocen lo básico\n"
            "🧠 Difícil: Para expertos en matemáticas\n"
            "🤖 ChatBot: Pregúntale a Dino cualquier cosa\n\n"
            "🎮 ¡Diviértete y aprende mientras juegas!"
        )

        mostrar_texto_adaptativo(self.pantalla, instrucciones, x_c, y_c, w_c, h_c,
                                 self.fonts["texto"], (30, 30, 30), centrado=True)

        # Animación dinos
        if pygame.time.get_ticks() - self.ultimo_cambio_dinos > 3000:
            self.dinos_actuales = random.sample(range(len(self.imagenes_dinos)), 3)
            self.ultimo_cambio_dinos = pygame.time.get_ticks()

        dino_y = int(520 * esc)
        dino_w, dino_h = int(120 * esc), int(80 * esc)
        espacio = int(80 * esc)
        total_w = 3 * dino_w + 2 * espacio
        x_ini = (self.pantalla.get_width() - total_w) // 2
        posiciones = [(x_ini + i * (dino_w + espacio), dino_y) for i in range(3)]

        animar_dinos(
            self.pantalla,
            [self.imagenes_dinos[i] for i in self.dinos_actuales],
            posiciones,
            esc,
            pygame.time.get_ticks()
        )

    def mostrar_chatbot(self):
        ancho, alto = self.pantalla.get_width(), self.pantalla.get_height()
        dibujar_caja_texto(self.pantalla, self.sx(80), self.sy(120), ancho - self.sx(160), alto - self.sy(180),
                           (245, 245, 255), radius=24)

        mostrar_texto_adaptativo(self.pantalla, "ChatBot Dino", self.sx(100), self.sy(140),
                                 ancho - self.sx(200), self.sy(60), pygame.font.SysFont("Segoe UI", 48, bold=True),
                                 (70, 130, 180), centrado=True)

        

    def mostrar_juegos(self, dificultad):
        self.dificultad_seleccionada = dificultad
        w_t, h_t = self.sx(640), self.sy(60)
        x_t = (self.pantalla.get_width() - w_t) // 2
        y_t = self.sy(110)
        dibujar_caja_texto(self.pantalla, x_t, y_t, w_t, h_t, (70, 130, 180))
        mostrar_texto_adaptativo(
            self.pantalla,
            f"Juegos de nivel {dificultad} 🎯",
            x_t, y_t, w_t, h_t,
            self.fonts["titulo"],
            (255, 255, 255),
            centrado=True
        )

        x, y = self.sx(100), self.sy(200)
        w, h = self.pantalla.get_width() - self.sx(200), self.pantalla.get_height() - self.sy(260)
        self.juego_rects = dibujar_caja_juegos(
            self.pantalla, x, y, w, h,
            juegos=JUEGOS_DISPONIBLES,
            recursos=self.images,
            color=(255, 255, 255),
            alpha=30,
            radius=24,
            margen=24,
            tam_caja_default=160,  # Updated parameter name to match animations.py
            fuente=self.fonts["texto"]
        )

    def handle_juegos_eventos(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and hasattr(self, "juego_rects"):
            for idx, rect in enumerate(self.juego_rects):
                if idx < len(JUEGOS_DISPONIBLES) and rect.collidepoint(event.pos):
                    juego = JUEGOS_DISPONIBLES[idx]
                    if callable(juego["clase"]):
                        instancia = juego["clase"](
                            self.pantalla, self.config, self.dificultad_seleccionada, self.fondo,
                            self.navbar, self.images, self.sounds,
                            return_to_menu=lambda: set_screen(self.screen_manager, JuegosScreen(self, self.dificultad_seleccionada))
                        )
                        set_screen(self.screen_manager, GameInstanceScreen(instancia))
                        return True
        return False

    def run(self):
        set_screen(self.screen_manager, HomeScreen(self))
        running = True
        last_time = pygame.time.get_ticks()
        FPS = 60

        while running:
            now = pygame.time.get_ticks()
            dt = (now - last_time) / 1000.0
            last_time = now

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    if (event.w, event.h) != (self.base_width, self.base_height):
                        self.base_width, self.base_height = event.w, event.h
                        self.pantalla = pygame.display.set_mode((self.base_width, self.base_height), pygame.RESIZABLE)
                        self.fondo.resize(self.base_width, self.base_height)
                        self._precache_fonts()

                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    resultado = self.navbar.handle_event(event, self.logo)
                    if resultado is not None:
                        destino = self.niveles[resultado]
                        if destino == "Home":
                            set_screen(self.screen_manager, HomeScreen(self))
                        elif destino in ("Fácil", "Normal", "Difícil"):
                            set_screen(self.screen_manager, JuegosScreen(self, destino))
                        elif destino == "ChatBot":
                            set_screen(self.screen_manager, BotScreen(self))

            self.tooltip_manager.update(pygame.mouse.get_pos())
            handle_event_screen(self.screen_manager, events)

            self.fondo.update(dt * FPS)
            self.fondo.draw(self.pantalla)

            update_screen(self.screen_manager, dt)
            draw_screen(self.screen_manager, self.pantalla)
            self.navbar.draw(self.pantalla, self.logo)

            pygame.display.flip()
            self.clock.tick(FPS)

def run_menu_principal(pantalla, fondo, images, sounds, config, screen_manager=None):
    menu = MenuPrincipal(pantalla, fondo, images, sounds, config, screen_manager)
    menu.run()
