import pygame
import random
import sys
from ui.components.utils import Boton, dibujar_caja_texto
from ui.navigation_bar import NavigationBar
from core.juego_base import JuegoBase, PALETA


def generar_problema_suma_resta(nivel):
    """Genera un problema de suma o resta con enunciado temático según el nivel"""
    if nivel == "Básico":
        a = random.randint(1, 10)
        b = random.randint(1, min(10, a))
        operacion = random.choice(['+', '-'])
        if operacion == '+':
            problema = f"Dino encontró {a} huevos en su cueva y luego encontró {b} más en el bosque.\n¿Cuántos huevos tiene en total?"
            respuesta = a + b
        else:
            problema = f"Dino tenía {a} huevos y usó {b} para hacer una tortilla.\n¿Cuántos huevos le quedan?"
            respuesta = a - b
    elif nivel == "Medio":
        a = random.randint(10, 20)
        b = random.randint(1, min(15, a))
        operacion = random.choice(['+', '-'])
        if operacion == '+':
            problema = f"Dino recolectó {a} frutas y luego encontró {b} más.\n¿Cuántas frutas tiene ahora?"
            respuesta = a + b
        else:
            problema = f"Dino tenía {a} piedras y perdió {b} en el camino.\n¿Cuántas piedras le quedan?"
            respuesta = a - b
    else:  # Avanzado
        a = random.randint(10, 30)
        b = random.randint(5, 15)
        c = random.randint(1, 10)
        operacion = random.choice(['++', '+-', '-+'])
        if operacion == '++':
            problema = f"Dino encontró {a} semillas, luego {b} más y después otras {c}.\n¿Cuántas semillas tiene en total?"
            respuesta = a + b + c
        elif operacion == '+-':
            problema = f"Dino tenía {a} hojas, encontró {b} más pero el viento se llevó {c}.\n¿Cuántas hojas tiene ahora?"
            respuesta = a + b - c
        else:
            problema = f"Dino tenía {a} nueces, dio {b} a sus amigos y luego encontró {c} más.\n¿Cuántas nueces tiene ahora?"
            respuesta = a - b + c
    return problema, respuesta


class JuegoSumaResta(JuegoBase):
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu=None):
        super().__init__('Dino Suma y Resta', pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        self.nivel_actual = self._nivel_from_dificultad(dificultad)
        self.puntuacion = 0
        self.jugadas_totales = 0
        self.tiempo_mensaje = 0
        self.mensaje = ""
        self.piedrita = images.get("piedrita") if images else None
        self.dino_img = images.get("dino1") if images else None
        self.cueva_img = images.get("cueva") if images else None
        self._ajustar_imagenes()
        self.opciones = []
        self.opcion_botones = []
        self.generar_problema()

    def _ajustar_imagenes(self):
        alto_img = int(self.ALTO * 0.25)
        if self.dino_img:
            self.dino_img = pygame.transform.smoothscale(self.dino_img, (alto_img, alto_img))
        if self.cueva_img:
            self.cueva_img = pygame.transform.smoothscale(self.cueva_img, (alto_img, alto_img))
        if self.piedrita:
            self.piedrita = pygame.transform.smoothscale(self.piedrita, (60, 60))

    def generar_problema(self):
        self.problema_actual, self.respuesta_correcta = generar_problema_suma_resta(self.nivel_actual)
        self.opciones = self.generar_opciones(self.respuesta_correcta)
        # Los botones se crean en draw con dibujar_opciones()

    def draw(self, surface=None):
        pantalla = surface if surface else self.pantalla
        self.pantalla = pantalla
        super().draw(surface)

        # Problema en caja decorativa
        texto_problem_y = self.navbar_height + 95
        altura_caja = 80
        dibujar_caja_texto(
            self.pantalla,
            self.ANCHO//2 - 350,
            texto_problem_y,
            700,
            altura_caja,
            (245, 245, 245, 200)
        )
        self.mostrar_texto(
            self.problema_actual,
            x=self.ANCHO//2 - 320,
            y=texto_problem_y + 10,
            w=640,
            h=altura_caja - 20,
            fuente=self.fuente,
            color=(20, 20, 80),
            centrado=True
        )

        # Imágenes decorativas
        alto_img = int(self.ALTO * 0.22)
        y_fila = texto_problem_y + altura_caja + 20
        if self.dino_img:
            self.pantalla.blit(self.dino_img, (60, y_fila))
        if self.cueva_img:
            self.pantalla.blit(self.cueva_img, (self.ANCHO - alto_img - 60, y_fila))
        if self.piedrita:
            espacio_total = self.ANCHO - 120 - alto_img * 2
            for i in range(3):
                x = 60 + alto_img + espacio_total * (i + 1) // 4
                self.pantalla.blit(self.piedrita, (x, y_fila + alto_img // 3))

        # Opciones (usa método base, botones responsivos y coloridos)
        y_btn = int(self.ALTO * 0.65)
        self.dibujar_opciones(y0=y_btn)

        # Feedback y puntaje
        self.dibujar_feedback()
        self.draw_animacion_estrellas()
        self.draw_particulas()
        self.mostrar_operacion()
       

    def handle_event(self, evento):
        super().handle_event(evento)
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for i, boton in enumerate(self.opcion_botones):
                if boton.rect.collidepoint(evento.pos):
                    self.jugadas_totales += 1
                    if self.opciones[i] == self.respuesta_correcta:
                        self.puntuacion += 1
                        self.mostrar_feedback(True)
                        self.crear_explosion_particulas(boton.rect.centerx, boton.rect.centery)
                    else:
                        self.mostrar_feedback(False, self.respuesta_correcta)
                    self.generar_problema()
                    return True
        return False

    def update(self, dt=0):
        self.update_animacion_estrellas()
        self.update_particulas()

    def on_resize(self, ancho, alto):
        self.ANCHO = ancho
        self.ALTO = alto
        self._ajustar_imagenes()

