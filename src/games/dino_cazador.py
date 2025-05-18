import pygame
import sys
import random
import math
from pygame.locals import *
from core.juego_base import JuegoBase  # Asegúrate de que la ruta sea correcta
from ui.components.utils import obtener_fuente, dibujar_caja_texto, mostrar_texto_adaptativo

def generar_problema_multiplicacion(nivel):
    """Genera un problema de multiplicación variado y dinámico según el nivel"""
    enunciados = {
        "Básico": [
            lambda a, b: (f"Un dinosaurio pone {a} huevos cada semana. ¿Cuántos huevos pondrá en {b} semanas?", a * b),
            lambda a, b: (f"Hay {a} dinosaurios y cada uno encuentra {b} piedras. ¿Cuántas piedras encuentran en total?", a * b),
            lambda a, b: (f"Cada dino tiene {a} garras y hay {b} dinos. ¿Cuántas garras hay en total?", a * b)
        ],
        "Medio": [
            lambda a, b: (f"Hay {a} nidos con {b} huevos cada uno. ¿Cuántos huevos hay en total?", a * b),
            lambda a, b: (f"Un grupo de {a} dinosaurios recoge {b} frutas cada uno. ¿Cuántas frutas recogen?", a * b),
            lambda a, b: (f"Cada dino da {a} pasos y hay {b} dinos. ¿Cuántos pasos en total?", a * b)
        ],
        "Avanzado": [
            lambda a, b, c: (f"Un dinosaurio come {a} hojas por día. Si hay {b} dinosaurios y comen durante {c} días, ¿cuántas hojas comerán en total?", a * b * c),
            lambda a, b, c: (f"Hay {a} huevos en cada nido, {b} nidos y {c} días para recogerlos. ¿Cuántos huevos en total?", a * b * c),
            lambda a, b, c: (f"Un dino corre {a} metros al día, hay {b} dinos y corren {c} días. ¿Cuántos metros corren en total?", a * b * c)
        ]
    }

    if nivel == "Básico":
        a, b = random.randint(1, 5), random.randint(1, 5)
        enunciado = random.choice(enunciados["Básico"])
        problema, respuesta = enunciado(a, b)
    elif nivel == "Medio":
        a, b = random.randint(2, 10), random.randint(2, 10)
        enunciado = random.choice(enunciados["Medio"])
        problema, respuesta = enunciado(a, b)
    else:
        a, b, c = random.randint(5, 15), random.randint(5, 10), random.randint(1, 5)
        enunciado = random.choice(enunciados["Avanzado"])
        problema, respuesta = enunciado(a, b, c)

    opciones = {respuesta}
    while len(opciones) < 3:
        d = respuesta + random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        if d > 0:
            opciones.add(d)
    return problema, respuesta, list(opciones)


class JuegoCazadorNumeros(JuegoBase):
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu=None):
        super().__init__('Cazador de Números', pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        self.nivel_actual = self._nivel_from_dificultad(dificultad)
        self.puntuacion = 0
        self.jugadas_totales = 0
        self.tiempo_mensaje = 0
        self.mensaje = ""
        self._ajustar_imagenes()
        self.init_responsive_ui()
        self.generar_problema()

    def _ajustar_imagenes(self):
        # Aquí puedes escalar imágenes si las usas, similar a dino_suma_resta o rescate_jurasico
        pass

    def init_responsive_ui(self):
        super().init_responsive_ui()
        sx, sy = self.sx, self.sy
        mx = sx(40)
        title_y, title_h = self.ui_elements["titulo_rect"][1], self.ui_elements["titulo_rect"][3]
        instr_y = title_y + title_h + sy(15)
        self.ui_elements.update({
            "instr_rect":      (mx, instr_y, self.ANCHO-2*mx, sy(40)),
            "img_area_top":    instr_y + sy(60),
            "img_area_h":      sy(120),
            "enunciado_rect":  (mx, instr_y + sy(60) + sy(120) + sy(10), self.ANCHO-2*mx, sy(60)),
            "opciones_y":      instr_y + sy(60) + sy(120) + sy(10) + sy(60) + sy(10)
        })
        self._scale_images()

    def _scale_images(self):
        """Pre-escalar imágenes y posiciones para _draw_images."""
        img_dino = self.images.get("dino3")
        img_fruta = self.images.get("fruta")
        if not img_dino or not img_fruta:
            return

        area_h = self.ui_elements["img_area_h"]
        # tamaños
        h_big = int(area_h * 0.8)
        mini = int(area_h * 0.35)
        # escalado único
        self.dino_big    = pygame.transform.smoothscale(img_dino,  (h_big,  h_big))
        self.fruta_big   = pygame.transform.smoothscale(img_fruta, (h_big,  h_big))
        self.fruta_mini  = pygame.transform.smoothscale(img_fruta, (mini,   mini))

        sep = mini + self.sx(10)
        centre = self.ANCHO // 2 - sep
        m = self.sx(20)   # reduce margen para acercar
        # precomputar posiciones
        self._img_pos = {
            "y":       self.ui_elements["img_area_top"] + area_h // 2,
            "x_dino":  centre - m - h_big,
            "x_fruta": centre + 3 * sep + m,
            "centres": [centre + i * sep for i in range(3)]
        }

    def generar_problema(self):
        self.problema_actual, self.respuesta_correcta, self.opciones = generar_problema_multiplicacion(self.nivel_actual)
        random.shuffle(self.opciones)
        self.mensaje = ""
        self.tiempo_mensaje = 0

    def handle_event(self, evento):
        super().handle_event(evento)
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for i, boton in enumerate(self.opcion_botones):
                if boton.rect.collidepoint(evento.pos):
                    self.jugadas_totales += 1
                    if int(boton.texto) == self.respuesta_correcta:
                        self.puntuacion += 1
                        self.racha_correctas += 1
                        self.mejor_racha = max(self.mejor_racha, self.racha_correctas)
                        self.crear_efecto_estrellas(boton.rect.center)
                        self.crear_explosion_particulas(boton.rect.centerx, boton.rect.centery)
                        self.mostrar_feedback(True)
                        pygame.time.set_timer(pygame.USEREVENT, 1200, True)
                    else:
                        self.racha_correctas = 0
                        self.mostrar_feedback(False, self.respuesta_correcta)
                    break
        elif evento.type == pygame.USEREVENT:
            self.generar_problema()

    def update(self, dt=None):
        super().update(dt)
        if self.tiempo_mensaje:
            self.tiempo_mensaje -= 1
            if self.tiempo_mensaje <= 0:
                self.mensaje = ""
        self.update_animacion_estrellas()
        self.update_particulas()

    def draw(self, surface=None):
        surf = surface or self.pantalla
        self.dibujar_fondo()
        self.mostrar_titulo()
        self._draw_instruccion(surf)
        self._draw_images(surf)
        self._draw_enunciado(surf)
        self._draw_opciones(surf)
        self._draw_feedback(surf)
        self.mostrar_puntaje(self.puntuacion, self.jugadas_totales, "Puntuación")
        self.mostrar_racha()

    def _draw_instruccion(self, surf):
        rect = self.ui_elements["instr_rect"]
        self.mostrar_texto(
            "¡Caza el número más grande!",
            *rect,
            fuente=obtener_fuente(self.sf(22)),
            color=(80, 80, 80),
            centrado=True
        )

    def _draw_images(self, surf):
        # blit pre-escalados y pre-posicionados
        y0 = self._img_pos["y"]
        for surf_img, x in (
            (self.dino_big,  self._img_pos["x_dino"]),
            (self.fruta_big, self._img_pos["x_fruta"])
        ):
            surf.blit(surf_img, (x, y0 - surf_img.get_height() // 2))

        h_mini = self.fruta_mini.get_height()
        for x in self._img_pos["centres"]:
            surf.blit(self.fruta_mini, (x, y0 - h_mini // 2))

    def _draw_enunciado(self, surf):
        rect = self.ui_elements["enunciado_rect"]
        self.mostrar_texto(
            self.problema_actual,
            *rect,
            fuente=obtener_fuente(self.sf(22)),
            color=(30, 30, 30),
            centrado=True
        )

    def _draw_opciones(self, surf):
        y0 = self.ui_elements["opciones_y"]
        self.dibujar_opciones(opciones=[str(n) for n in self.opciones], y0=y0)

    def _draw_feedback(self, surf):
        self.dibujar_feedback()
        self.draw_animacion_estrellas()
        self.draw_particulas()

