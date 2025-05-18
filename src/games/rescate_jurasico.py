import pygame
import random
from pygame.locals import *
from core.juego_base import JuegoBase
from ui.components.utils import obtener_fuente

def generar_problema_division(nivel):
    if nivel == "Básico":
        b = random.randint(1, 5)
        a = b * random.randint(1, 5)
        problema = f"Dino tiene {a} bayas. Si las reparte en {b} grupos iguales, ¿cuántas bayas habrá en cada grupo?"
        respuesta = a // b
    elif nivel == "Medio":
        b = random.randint(2, 5)
        a = b * random.randint(3, 8)
        problema = f"Dino tiene {a} bayas y quiere repartirlas entre {b} amigos. ¿Cuántas bayas recibirá cada amigo?"
        respuesta = a // b
    else:  # Avanzado
        b = random.randint(3, 6)
        a = b * random.randint(5, 10)
        c = random.randint(1, 3)
        problema = f"Dino tiene {a} bayas. Si las reparte en {b} grupos iguales y luego come {c} de un grupo, ¿cuántas bayas le quedan en ese grupo?"
        respuesta = (a // b) - c
    return problema, respuesta

class JuegoRescate(JuegoBase):
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        super().__init__('Rescate Jurásico', pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        self.puntuacion = 0
        self.jugadas_totales = 0
        self.posicion_dino = 0
        self.total_pasos = 3

        # Referencias a las imágenes originales
        self.dino_mama_orig = images.get("dino5")
        self.dino_bebe_orig = images.get("dino2")
        self.roca_orig     = images.get("roca")

        self._ajustar_imagenes()
        self.init_responsive_ui()
        self.generar_problema()

    def init_responsive_ui(self):
        super().init_responsive_ui()
        sx, sy = self.sx, self.sy
        mx = sx(40)
        self.ui_elements.update({
            "instr_rect":      (mx, self.navbar_height+sy(50), self.ANCHO-2*mx, sy(40)),
            "img_area_top":    self.navbar_height + sy(100),
            "img_area_h":      sy(120),
            "spacing":         sx(30),
            "roca_espacio":    sx(80),
            "dino_size":       (sx(80), sy(80)),
            "roca_size":       (sx(60), sy(60)),
            "enunciado_rect":  (mx, self.navbar_height+sy(100)+sy(120)+sy(10), self.ANCHO-2*mx, sy(60)),
            "opciones_y":      self.navbar_height+sy(100)+sy(120)+sy(10)+sy(60)+sy(10)
        })

    def _ajustar_imagenes(self):
        """Escala dino mamá, dino bebé y roca según la resolución."""
        sx, sy = self.sx, self.sy
        dw, dh = int(sx(80)), int(sy(80))
        rw, rh = int(sx(60)), int(sy(60))

        self.dino_mama_img = (pygame.transform.smoothscale(self.dino_mama_orig, (dw, dh))
                              if self.dino_mama_orig else None)
        self.dino_bebe_img = (pygame.transform.smoothscale(self.dino_bebe_orig, (dw, dh))
                              if self.dino_bebe_orig else None)
        self.roca_img      = (pygame.transform.smoothscale(self.roca_orig, (rw, rh))
                              if self.roca_orig else None)

    def on_resize(self, ancho, alto):
        self.ANCHO, self.ALTO = ancho, alto
        self.scaler.update(ancho, alto)
        self.init_responsive_ui()
        self._ajustar_imagenes()

    def generar_problema(self):
        nivel = self._nivel_from_dificultad(self.dificultad)
        self.problema_actual, self.respuesta_correcta = generar_problema_division(nivel)
        self.opciones = self.generar_opciones(self.respuesta_correcta, cantidad=3)
        random.shuffle(self.opciones)
        self.mensaje = ""
        self.tiempo_mensaje = 0

    def handle_event(self, evento):
        super().handle_event(evento)
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for btn in self.opcion_botones:
                if btn.rect.collidepoint(evento.pos):
                    self.jugadas_totales += 1
                    correcto = int(btn.texto) == self.respuesta_correcta
                    if correcto:
                        self.puntuacion += 1
                        self.posicion_dino += 1
                        self.racha_correctas += 1
                        self.mejor_racha = max(self.mejor_racha, self.racha_correctas)
                        self.crear_efecto_estrellas(btn.rect.center)
                        self.crear_explosion_particulas(btn.rect.centerx, btn.rect.centery)
                        self.mostrar_feedback(True)
                        pygame.time.set_timer(pygame.USEREVENT, 1500, True)
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
            "¡Ayuda a mamá dinosaurio a rescatar a su bebé!",
            *rect,
            fuente=obtener_fuente(self.sf(22)),
            color=(80, 80, 80),
            centrado=True
        )

    def _draw_images(self, surf):
        ie_top = self.ui_elements["img_area_top"]
        ie_h   = self.ui_elements["img_area_h"]
        sp     = self.ui_elements["spacing"]
        re     = self.ui_elements["roca_espacio"]
        dw, dh = self.ui_elements["dino_size"]
        rw, rh = self.ui_elements["roca_size"]
        pasos  = self.total_pasos

        block_w = dw + sp + pasos * re + sp + dw
        start_x = (self.ANCHO - block_w) // 2
        center_y = ie_top + ie_h // 2

        if self.dino_mama_img:
            surf.blit(self.dino_mama_img, (start_x, center_y - dh // 2))
        for i in range(pasos):
            if self.roca_img:
                surf.blit(self.roca_img, (start_x + dw + sp + i * re, center_y - rh // 2))
        if self.dino_bebe_img:
            surf.blit(self.dino_bebe_img, (start_x + dw + sp + pasos * re + sp, center_y - dh // 2 + self.sy(10)))

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
        self.dibujar_opciones(y0=y0)

    def _draw_feedback(self, surf):
        self.dibujar_feedback()
        self.draw_animacion_estrellas()
        self.draw_particulas()
