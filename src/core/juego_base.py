import pygame
import random
from ui.components.utils import (
    mostrar_texto_adaptativo, Boton, obtener_fuente, render_text_cached,
    dibujar_caja_texto, TooltipManager
)
from ui.components.emoji import mostrar_alternativo_adaptativo
from core.decoration.effects import EffectsMixin
from core.decoration.background_game import FondoAnimado
from core.decoration.paleta import PALETA_LISTA as PALETA
from core.scale.responsive_scaler_basic import ResponsiveScaler
from core.decoration.helpers import (
    mostrar_texto, mostrar_titulo, mostrar_instrucciones, mostrar_puntaje,
    dibujar_opciones, mostrar_victoria, mostrar_operacion, mostrar_racha
)

class JuegoBase(EffectsMixin):
    def __init__(self, nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        self.nombre = nombre
        self.pantalla = pantalla
        self.config = config
        self.dificultad = dificultad
        self.fondo = fondo
        self.navbar = navbar
        self.images = images
        self.sounds = sounds
        self.return_to_menu = return_to_menu

        self.ANCHO = pantalla.get_width()
        self.ALTO = pantalla.get_height()
        self.scaler = ResponsiveScaler(1280, 720)
        self.scaler.update(self.ANCHO, self.ALTO)
        self.sx = self.scaler.scale_x_value
        self.sy = self.scaler.scale_y_value
        self.sf = self.scaler.scale_font_size

        self.fuente_titulo = obtener_fuente(self.sf(36), negrita=True)
        self.fuente = obtener_fuente(self.sf(20))
        self.reloj = pygame.time.Clock()
        self.navbar_height = 0
        self._update_navbar_height()
        self.tooltip_manager = TooltipManager(delay=1.0)
        pygame.display.set_caption(f"{self.nombre} - {self.dificultad}")
        self.opcion_botones = []
        self.ui_elements = {}
        self.init_responsive_ui()
        self.racha_correctas = 0
        self.mejor_racha = 0
        self.operacion_actual = ""
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.mensaje_color = (255, 255, 255, 220)
        self.mensaje_animacion = 1.0
        self.sonido_activado = True
        self.estrellas = []
        self.particulas = []
        self.estrella_img = None
        self.animacion_activa = False
        self.tiempo_animacion = 0
        self.fondo_animado = FondoAnimado(self.pantalla, self.navbar_height)
        self.fondo_animado.set_escaladores(self.sx, self.sy)
        self.fondo_animado.resize(self.ANCHO, self.ALTO)

    def mostrar_racha(self, rect=None):
        mostrar_racha(self.pantalla, self.ANCHO, self.ALTO, self.sx, self.sy, self.racha_correctas, self.mejor_racha, rect)

    def mostrar_operacion(self, rect=None):
        mostrar_operacion(self.pantalla, self.ANCHO, self.navbar_height, self.sx, self.sy, self.operacion_actual, self.sf, rect)

    def mostrar_texto(self, texto, x, y, w, h, fuente=None, color=(30,30,30), centrado=False):
        mostrar_texto(self.pantalla, texto, x, y, w, h, fuente or self.fuente, color, centrado)

    def mostrar_titulo(self):
        mostrar_titulo(self.pantalla, self.nombre, self.dificultad, self.fuente_titulo, self.ui_elements, self.navbar_height, self.sy, self.ANCHO)

    def mostrar_puntaje(self, juegos_ganados, juegos_totales, frase="¡Puntaje!"):
        mostrar_puntaje(self.pantalla, juegos_ganados, juegos_totales, self.fuente, self.sy, self.sx, self.ALTO, self.ui_elements, frase)

    def dibujar_opciones(self, opciones=None, tooltips=None, estilo="flat", border_radius=None, x0=None, y0=None, espacio=None):
        dibujar_opciones(
            self.pantalla, opciones or getattr(self, "opciones", []), self.fuente, self.sx, self.sy,
            self.ANCHO, self.ALTO, PALETA, self.opcion_botones, tooltips, estilo, border_radius, x0, y0, espacio, getattr(self, "tooltip_manager", None)
        )

    def mostrar_victoria(self, carta_rects, color_panel=(255, 255, 224), color_borde=(255, 215, 0)):
        mostrar_victoria(
            self.pantalla, self.sx, self.sy, self.ANCHO, self.ALTO, self.fuente_titulo, self.fuente,
            mostrar_alternativo_adaptativo, mostrar_texto_adaptativo, Boton, dibujar_caja_texto, carta_rects, color_panel, color_borde
        )

    def mostrar_instrucciones(self, fuente_pequeña, texto=None):
        mostrar_instrucciones(self.pantalla, self.sx, self.sy, self.ALTO, self.ANCHO, fuente_pequeña, texto)

    def init_responsive_ui(self):
        self.ui_elements = {
            "titulo_rect": (0, self.navbar_height + self.sy(30), self.ANCHO, self.sy(60)),
            "feedback_rect": self.scaler.get_centered_rect(500, 50, vertical_offset=self.ALTO//2 - 50),
            "puntaje_rect": (self.sx(18), self.ALTO - self.sy(48) - self.sy(18), 
                            self.sx(180), self.sy(48))
        }

    def _nivel_from_dificultad(self, dificultad):
        if dificultad == "Fácil":
            return "Básico"
        elif dificultad == "Normal":
            return "Medio"
        else:
            return "Avanzado"

    def _update_navbar_height(self):
        if self.navbar and hasattr(self.navbar, "get_height"):
            self.navbar_height = self.navbar.get_height()
        elif self.navbar and hasattr(self.navbar, "height"):
            self.navbar_height = self.navbar.height
        else:
            self.navbar_height = self.sy(60)

    def cargar_imagenes(self):
        pass

    def dibujar_fondo(self):
        if self.pantalla:
            self.fondo_animado.update()
            self.fondo_animado.draw()

    def generar_opciones(self, respuesta: int, cantidad: int = 3) -> list[int]:
        opciones = {respuesta}
        posibles = set(range(max(0, respuesta - 10), respuesta + 11)) - {respuesta}
        while len(opciones) < cantidad and posibles:
            op = random.choice(list(posibles))
            opciones.add(op)
            posibles.remove(op)
        while len(opciones) < cantidad:
            op = respuesta + random.randint(1, 20)
            opciones.add(op)
        resultado = list(opciones)
        random.shuffle(resultado)
        return resultado

    def handle_event(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            if self.return_to_menu:
                self.return_to_menu()
                pygame.display.set_caption("jugando con dino")
        if evento.type == pygame.VIDEORESIZE:
            self.ANCHO, self.ALTO = evento.w, evento.h
            self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO), pygame.RESIZABLE)
            self._update_navbar_height()
            self.scaler.update(self.ANCHO, self.ALTO)
            self.fuente_titulo = obtener_fuente(self.sf(36), negrita=True)
            self.fuente = obtener_fuente(self.sf(20))
            self.init_responsive_ui()
            self.fondo_animado.set_escaladores(self.sx, self.sy)
            self.fondo_animado.resize(self.ANCHO, self.ALTO)
            self.on_resize(self.ANCHO, self.ALTO)
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for btn in self.opcion_botones:
                if btn.handle_event(evento):
                    break

    def on_resize(self, ancho, alto):
        pass

    def update(self, dt=None):
        self.fondo_animado.update()

    def draw(self, surface):
        surface = surface or self.pantalla
        self.dibujar_fondo()
        self.mostrar_titulo()
        # Usa los atributos propios si existen, si no usa config
        if hasattr(self, "puntuacion") and hasattr(self, "jugadas_totales"):
            self.mostrar_puntaje(self.puntuacion, self.jugadas_totales)
        else:
            self.mostrar_puntaje(self.config["juegos_ganados"], self.config["juegos_totales"])
        self.mostrar_racha()

