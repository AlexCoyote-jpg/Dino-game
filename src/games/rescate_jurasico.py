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
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.mensaje_color = (255, 255, 255, 220)
        self.mensaje_animacion = 1.0
        self.racha_correctas = 0
        self.mejor_racha = 0
        self.cargar_imagenes()
        self.generar_problema()

    def cargar_imagenes(self):
        self.dino_mama_img = self.images.get("dino5")   # Izquierda
        self.dino_bebe_img = self.images.get("dino2")     # Derecha
        self.roca_img = self.images.get("roca")           # Rocas centrales

    def generar_problema(self):
        nivel = self._nivel_from_dificultad(self.dificultad)
        self.problema_actual, self.respuesta_correcta = generar_problema_division(nivel)
        self.opciones = self.generar_opciones(self.respuesta_correcta, cantidad=3)
        random.shuffle(self.opciones)
        self.mensaje = ""
        self.tiempo_mensaje = 0

    def mostrar_feedback(self, correcto, respuesta_correcta=None):
        if correcto:
            self.mensaje = "¡Correcto!"
            self.mensaje_color = (0, 120, 0)
        else:
            self.mensaje = f"Incorrecto. Respuesta: {respuesta_correcta}"
            self.mensaje_color = (180, 40, 40)
        self.tiempo_mensaje = 60  # duración en frames

    def handle_event(self, evento):
        super().handle_event(evento)
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for btn in self.opcion_botones:
                if btn.rect.collidepoint(evento.pos):
                    self.jugadas_totales += 1
                    es_correcto = int(btn.texto) == self.respuesta_correcta
                    if es_correcto:
                        self.puntuacion += 1
                        self.posicion_dino += 1
                        self.racha_correctas += 1
                        self.mejor_racha = max(self.mejor_racha, self.racha_correctas)
                        # Activar animaciones de estrellas y partículas
                        self.crear_efecto_estrellas(btn.rect.center)
                        self.crear_explosion_particulas(btn.rect.centerx, btn.rect.centery)
                        self.mostrar_feedback(True)
                        if self.posicion_dino > self.total_pasos:
                            self.posicion_dino = 0
                        self.generar_problema()
                    else:
                        self.racha_correctas = 0
                        self.mostrar_feedback(False, self.respuesta_correcta)
                    break

    def update(self, dt=None):
        super().update(dt)
        if self.tiempo_mensaje:
            self.tiempo_mensaje -= 1
            if self.tiempo_mensaje <= 0:
                self.mensaje = ""
        self.update_animacion_estrellas()
        self.update_particulas()

    def draw(self, surface=None):
        destino = surface if surface is not None else self.pantalla
        self.dibujar_fondo()

        # Variables de escalado
        sx, sy, sf = self.sx, self.sy, self.sf
        margen_x = sx(40)
        area_top = self.navbar_height + sy(20)
        ancho_area = self.ANCHO - 2 * margen_x

        # Mostrar título e instrucciones
        self.mostrar_titulo()
        self.mostrar_texto(
            "¡Ayuda a mamá dinosaurio a rescatar a su bebé!",
            x=margen_x,
            y=area_top + sy(50),
            w=ancho_area,
            h=sy(40),
            fuente=obtener_fuente(sf(22)),
            color=(80, 80, 80),
            centrado=True
        )

        # Área central de imágenes
        area_img_y = area_top + sy(100)
        area_img_h = sy(120)
        roca_espacio = sx(80)
        roca_w, roca_h = sx(60), sy(60)
        dino_w, dino_h = sx(80), sy(80)
        block_width = dino_w + sx(30) + self.total_pasos * roca_espacio + sx(30) + dino_w
        start_x = (self.ANCHO - block_width) // 2

        # Dibujar mamá dino
        if self.dino_mama_img:
            img_mama = pygame.transform.smoothscale(self.dino_mama_img, (int(dino_w), int(dino_h)))
            destino.blit(img_mama, (start_x, area_img_y + area_img_h//2 - dino_h//2))

        # Dibujar rocas centrales
        roca_start_x = start_x + dino_w + sx(30)
        if self.roca_img:
            img_roca = pygame.transform.smoothscale(self.roca_img, (int(roca_w), int(roca_h)))
            for i in range(self.total_pasos):
                x = roca_start_x + i * roca_espacio
                destino.blit(img_roca, (x, area_img_y + area_img_h//2 - roca_h//2))

        # Dibujar bebé dino
        bebe_x = roca_start_x + self.total_pasos * roca_espacio + sx(30)
        if self.dino_bebe_img:
            img_bebe = pygame.transform.smoothscale(self.dino_bebe_img, (int(dino_w), int(dino_h)))
            destino.blit(img_bebe, (bebe_x, area_img_y + area_img_h//2 - dino_h//2 + sy(10)))

        # Mostrar enunciado del problema
        enunciado_y = area_img_y + area_img_h + sy(10)
        self.mostrar_texto(
            self.problema_actual,
            x=margen_x,
            y=enunciado_y,
            w=ancho_area,
            h=sy(60),
            fuente=obtener_fuente(sf(22)),
            color=(30, 30, 30),
            centrado=True
        )

        # Dibujar opciones de respuesta
        self.dibujar_opciones(y0=enunciado_y + sy(60) + sy(10))
        
        # Mostrar feedback y animaciones
        self.dibujar_feedback()
        self.draw_animacion_estrellas()
        self.draw_particulas()

        # Mostrar puntaje y racha
        self.mostrar_puntaje(self.puntuacion, self.jugadas_totales, "Puntuación")
        self.mostrar_racha()
