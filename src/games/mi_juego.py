import pygame
import random
from core.juego_base import JuegoBase
from ui.components.utils import obtener_fuente

def generar_problema():
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    op = random.choice(["+", "-"])
    if op == "+":
        resultado = a + b
    else:
        resultado = a - b
    texto = f"{a} {op} {b} = ?"
    return texto, resultado

class MiJuego(JuegoBase):
    def __init__(self, pantalla, config=None, dificultad=1, fondo=None, navbar=None, images=None, sounds=None, return_to_menu=None):
        nombre = "DinoMath"
        config = config or {}
        images = images or {}
        sounds = sounds or {}
        return_to_menu = return_to_menu or (lambda: None)
        super().__init__(nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)

        # preparar lista de problemas
        self.problemas = [generar_problema() for _ in range(10)]
        self.indice = 0
        self.puntaje = 0

        # fuente para instrucciones
        self.fuente_instrucciones = obtener_fuente(self.sf(16))
        # iniciar primer problema
        self.siguiente_problema()
        # UI responsiva
        self.init_responsive_ui()

    def init_responsive_ui(self):
        super().init_responsive_ui()
        self.ui_elements.update({
            "problema_rect": (
                self.sx(100),
                self.navbar_height + self.sy(80),
                self.ANCHO - self.sx(200),
                self.sy(80)
            ),
            "opciones_y": self.ALTO // 2,
            "instrucciones_rect": (
                self.sx(50),
                self.ALTO - self.sy(80),
                self.ANCHO - self.sx(100),
                self.sy(40)
            )
        })

    def on_resize(self, ancho, alto):
        super().on_resize(ancho, alto)
        self.fuente_instrucciones = obtener_fuente(self.sf(16))
        self.init_responsive_ui()

    def siguiente_problema(self):
        if self.indice < len(self.problemas):
            texto, resultado = self.problemas[self.indice]
            self.operacion_actual = texto
            self.respuesta_correcta = resultado
            self.opciones = self.generar_opciones(resultado, 3)
        else:
            self.operacion_actual = "¡Juego terminado!"
            self.opciones = []

    def handle_event(self, evento):
        super().handle_event(evento)
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for i, boton in enumerate(self.opcion_botones):
                if boton.collidepoint(evento.pos):
                    try:
                        valor = int(boton.texto)
                    except:
                        valor = None
                    ok = (valor == getattr(self, "respuesta_correcta", None))
                    self.mostrar_feedback(ok, respuesta_correcta=self.respuesta_correcta if not ok else None)
                    if ok:
                        self.puntaje += 1
                    self.indice += 1
                    self.siguiente_problema()
                    break

    def update(self, dt=None):
        # sincronizar puntaje y total
        self.puntuacion = self.puntaje
        self.total_preguntas = len(self.problemas)
        super().update(dt)

    def draw(self, surface=None):
        surface = surface or self.pantalla
        # fondo y título
        self.dibujar_fondo()
        self.mostrar_titulo()
        # mostrar problema
        x, y, w, h = self.ui_elements["problema_rect"]
        self.mostrar_texto(self.operacion_actual, x, y, w, h, fuente=self.fuente, centrado=True)
        # opciones
        self.dibujar_opciones(opciones=self.opciones, y0=self.ui_elements["opciones_y"])
        # puntaje y racha
        self.mostrar_puntaje(self.puntuacion, self.total_preguntas)
        self.mostrar_racha()
        # instrucciones
        ix, iy, iw, ih = self.ui_elements["instrucciones_rect"]
        self.mostrar_texto(
            "Haz clic en la respuesta correcta. ESC para menú.",
            ix, iy, iw, ih,
            fuente=self.fuente_instrucciones,
            color=(100,100,100),
            centrado=True
        )
