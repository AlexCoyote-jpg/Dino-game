import pygame
import random
import sys
from ui.components.utils import Boton, dibujar_caja_texto
from ui.navigation_bar import NavigationBar
from core.juego_base import JuegoBase, PALETA


def generar_problema_suma_resta(nivel):
    if nivel == "Básico":
        a = random.randint(1, 10)
        b = random.randint(1, min(10, a))
        operacion = random.choice(['+', '-'])
        if operacion == '+':
            return (f"Dino encontró {a} huevos en su cueva y luego encontró {b} más en el bosque.\n"
                    f"¿Cuántos huevos tiene en total?", a + b)
        else:
            return (f"Dino tenía {a} huevos y usó {b} para hacer una tortilla.\n"
                    f"¿Cuántos huevos le quedan?", a - b)

    elif nivel == "Medio":
        a = random.randint(10, 20)
        b = random.randint(1, min(15, a))
        operacion = random.choice(['+', '-'])
        if operacion == '+':
            return (f"Dino recolectó {a} frutas y luego encontró {b} más.\n"
                    f"¿Cuántas frutas tiene ahora?", a + b)
        else:
            return (f"Dino tenía {a} piedras y perdió {b} en el camino.\n"
                    f"¿Cuántas piedras le quedan?", a - b)

    else:  # Avanzado
        a = random.randint(10, 30)
        b = random.randint(5, 15)
        c = random.randint(1, 10)
        operacion = random.choice(['++', '+-', '-+'])
        if operacion == '++':
            return (f"Dino encontró {a} semillas, luego {b} más y después otras {c}.\n"
                    f"¿Cuántas semillas tiene en total?", a + b + c)
        elif operacion == '+-':
            return (f"Dino tenía {a} hojas, encontró {b} más pero el viento se llevó {c}.\n"
                    f"¿Cuántas hojas tiene ahora?", a + b - c)
        else:
            return (f"Dino tenía {a} nueces, dio {b} a sus amigos y luego encontró {c} más.\n"
                    f"¿Cuántas nueces tiene ahora?", a - b + c)


class JuegoSumaResta(JuegoBase):
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu=None):
        super().__init__('Dino Suma y Resta', pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        self.nivel_actual = self._nivel_from_dificultad(dificultad)
        self.puntuacion = 0
        self.jugadas_totales = 0
        self.tiempo_mensaje = 0
        self.mensaje = ""
        self.dino_img_orig = images.get("dino1") if images else None
        self.cueva_img_orig = images.get("cueva") if images else None
        self.piedrita_orig = images.get("piedrita") if images else None
        self._ajustar_imagenes()
        self.generar_problema()

    def _ajustar_imagenes(self):
        # Calcula nuevas dimensiones
        nuevo_dino_w = min(int(self.sx(120)), 140)
        nuevo_dino_h = min(int(self.sy(120)), 140)
        nuevo_piedrita_w = min(int(self.sx(44)), 48)
        nuevo_piedrita_h = min(int(self.sy(44)), 48)

        # Evita reprocesar si no cambió el tamaño
        if (
            hasattr(self, 'dino_w') and
            self.dino_w == nuevo_dino_w and
            self.dino_h == nuevo_dino_h and
            self.piedrita_w == nuevo_piedrita_w and
            self.piedrita_h == nuevo_piedrita_h
        ):
            return  # No recalcular transformaciones

        # Asigna las dimensiones actualizadas
        self.dino_w, self.dino_h = nuevo_dino_w, nuevo_dino_h
        self.cueva_w, self.cueva_h = self.dino_w, self.dino_h
        self.piedrita_w, self.piedrita_h = nuevo_piedrita_w, nuevo_piedrita_h

        # Transforma solo si hay imágenes originales
        if self.dino_img_orig:
            self.dino_img = pygame.transform.smoothscale(self.dino_img_orig, (self.dino_w, self.dino_h))
        if self.cueva_img_orig:
            self.cueva_img = pygame.transform.smoothscale(self.cueva_img_orig, (self.cueva_w, self.cueva_h))
        if self.piedrita_orig:
            self.piedrita = pygame.transform.smoothscale(self.piedrita_orig, (self.piedrita_w, self.piedrita_h))

    def generar_problema(self):
        self.problema_actual, self.respuesta_correcta = generar_problema_suma_resta(self.nivel_actual)
        self.opciones = self.generar_opciones(self.respuesta_correcta)

    def draw(self, surface=None):
        pantalla = surface if surface else self.pantalla
        self.pantalla = pantalla
        super().draw(surface)

        self.dibujar_titulo_y_instruccion()
        self.dibujar_imagenes()
        self.dibujar_enunciado()
        self.dibujar_opciones_respuesta()
        self.dibujar_feedback_y_efectos()

    def dibujar_titulo_y_instruccion(self):
        margen_x = self.sx(40)
        area_top = self.navbar_height + self.sy(30)  # Más espacio debajo de la navbar
        ancho_area = self.ANCHO - 2 * margen_x

        # Título
        self.mostrar_titulo()

        # Instrucción, más separada del título
        instruccion_y = area_top + self.sy(50)
        self.mostrar_texto(
            "\u00a1Ayuda a Dino a resolver la suma o resta!",
            margen_x,
            instruccion_y,
            ancho_area,
            self.sy(36),
            self.fuente,
            (80, 80, 80),
            True
        )

    def dibujar_imagenes(self):
        margen_x = self.sx(40)
        area_top = self.navbar_height + self.sy(110)  # Un poco más arriba para dar espacio al enunciado
        area_img_h = self.sy(140)
        espacio_entre = self.sx(170)  # Aumenta la separación entre dino y cueva
        block_width = self.dino_w + espacio_entre + self.cueva_w
        start_x = (self.ANCHO - block_width) // 2
        area_img_y = area_top

        # Centrado vertical de las imágenes en el área asignada
        dino_y = area_img_y + area_img_h // 2 - self.dino_h // 2
        cueva_y = area_img_y + area_img_h // 2 - self.cueva_h // 2

        # Coordenadas de dino y cueva
        dino_x = start_x
        cueva_x = start_x + self.dino_w + espacio_entre

        # Dibujar dino y cueva
        if self.dino_img:
            self.pantalla.blit(self.dino_img, (dino_x, dino_y))
        if self.cueva_img:
            self.pantalla.blit(self.cueva_img, (cueva_x, cueva_y))

        # Piedritas centradas entre dino y cueva, alineadas un poco arriba de los pies del dino
        if self.piedrita:
            n_piedritas = 3
            # Centro horizontal entre dino y cueva
            centro_piedritas_x = (dino_x + self.dino_w + cueva_x) // 2
            # Un poco arriba de los pies del dino (ajusta sy(20) según lo que veas mejor)
            piedritas_y = dino_y + self.dino_h - self.piedrita_h - self.sy(20)

            total_piedritas_w = n_piedritas * self.piedrita_w + (n_piedritas - 1) * self.sx(8)
            inicio_x = centro_piedritas_x - total_piedritas_w // 2

            for i in range(n_piedritas):
                x = inicio_x + i * (self.piedrita_w + self.sx(8))
                self.pantalla.blit(self.piedrita, (x, piedritas_y))

    def dibujar_enunciado(self):
        margen_x = self.sx(40)
        area_top = self.navbar_height + self.sy(20)
        ancho_area = self.ANCHO - 2 * margen_x
        enunciado_y = area_top + self.sy(70) + self.sy(120) + self.sy(10)
        self.mostrar_texto(self.problema_actual, margen_x, enunciado_y, ancho_area, self.sy(70),
                           self.fuente, (20, 20, 80), True)

    def dibujar_opciones_respuesta(self):
        y_btn = self.navbar_height + self.sy(300)
        self.dibujar_opciones(y0=y_btn)

    def dibujar_feedback_y_efectos(self):
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
                        self.generar_problema()
                    else:
                        self.mostrar_feedback(False, self.respuesta_correcta)
                    return True
        return False

    def update(self, dt=0):
        self.update_animacion_estrellas()
        self.update_particulas()

    def on_resize(self, ancho, alto):
        self.ANCHO = ancho
        self.ALTO = alto
        self._ajustar_imagenes()

    def cambiar_imagen_dino(self, nueva_img):
        self.dino_img_orig = nueva_img
        self._ajustar_imagenes()

    def cambiar_imagen_cueva(self, nueva_img):
        self.cueva_img_orig = nueva_img
        self._ajustar_imagenes()

    def cambiar_imagen_piedrita(self, nueva_img):
        self.piedrita_orig = nueva_img
        self._ajustar_imagenes()

    def generar_opciones(self, respuesta, cantidad=4):
        opciones = {respuesta}
        while len(opciones) < cantidad:
            delta = random.choice([-3, -2, -1, 1, 2, 3])
            distractor = respuesta + delta
            opciones.add(distractor)
        return random.sample(list(opciones), k=cantidad)
