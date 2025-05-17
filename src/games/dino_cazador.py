import pygame
import sys
import random
import math
from pygame.locals import *
from core.juego_base import JuegoBase  # Asegúrate de que la ruta sea correcta
from ui.components.utils import obtener_fuente, dibujar_caja_texto, mostrar_texto_adaptativo

def generar_problema_multiplicacion(nivel):
    """Genera un problema de multiplicación según el nivel"""
    if nivel == "Básico":
        a = random.randint(1, 5)
        b = random.randint(1, 5)
        problema = f"Un dinosaurio pone {a} huevos cada semana. ¿Cuántos huevos pondrá en {b} semanas?"
        respuesta = a * b
        operacion = f"{a} × {b} = ?"
    elif nivel == "Medio":
        a = random.randint(2, 10)
        b = random.randint(2, 10)
        problema = f"Hay {a} nidos con {b} huevos cada uno. ¿Cuántos huevos hay en total?"
        respuesta = a * b
        operacion = f"{a} × {b} = ?"
    else:  # Avanzado
        a = random.randint(5, 15)
        b = random.randint(5, 10)
        c = random.randint(1, 5)
        problema = f"Un dinosaurio come {a} hojas por día. Si hay {b} dinosaurios y comen durante {c} días, ¿cuántas hojas comerán en total?"
        respuesta = a * b * c
        operacion = f"{a} × {b} × {c} = ?"
    
    return problema, respuesta, operacion


class JuegoCazadorNumeros(JuegoBase):
    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        super().__init__('Dino Cazador de Números', pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        self.problema_actual = ""
        self.respuesta_correcta = None
        self.opciones = []
        self.puntuacion = 0
        self.jugadas_totales = 0
        self.tiempo_mensaje = 0
        self.mensaje = ""
        self.opcion_botones = []
        
        # Elementos para animación de estrellas
        self.estrellas = []
        self.estrella_img = None
        self.tiempo_animacion = 0
        self.animacion_activa = False
        
        # Inicializar elementos UI responsivos
        self.init_responsive_ui()
        
        # Cargar recursos y generar primer problema
        self.cargar_imagenes()
        self.generar_problema()

    def init_responsive_ui(self):
        """Inicializa elementos UI específicos de este juego."""
        super().init_responsive_ui()  # Llamar al método de la clase base primero
        
        # Añadir elementos específicos de este juego
        self.ui_elements.update({
            "enunciado_rect": (
                self.sx(40), 
                self.navbar_height + self.sy(100), 
                self.ANCHO - self.sx(80), 
                max(self.sy(90), int(self.ALTO * 0.13))
            ),
            "operacion_rect": (
                self.ANCHO - self.sx(200), 
                self.navbar_height + self.sy(50), 
                self.sx(180), 
                self.sy(40)
            ),
            "opciones_y": self.navbar_height + self.sy(100) + max(self.sy(90), int(self.ALTO * 0.13)) + self.sy(30),
            "racha_rect": (
                self.ANCHO - self.sx(200), 
                self.ALTO - self.sy(70), 
                self.sx(180), 
                self.sy(50)
            ),
            "dino_pos": (
                self.sx(20), 
                self.ALTO - self.sy(150)
            )
        })

    def cargar_imagenes(self):
        # Ajusta el tamaño de las imágenes para que entren bien en pantalla
        dino_img = self.images.get("dino3")
        fruta_img = self.images.get("fruta")
        ancho_max = int(self.ANCHO * 0.13)  # 13% del ancho de pantalla
        alto_max = int(self.ALTO * 0.13)    # 13% del alto de pantalla

        if dino_img:
            ow, oh = dino_img.get_size()
            escala = min(ancho_max / ow, alto_max / oh, 1)
            nuevo_w = int(ow * escala)
            nuevo_h = int(oh * escala)
            self.dino_img = pygame.transform.smoothscale(dino_img, (nuevo_w, nuevo_h))
        else:
            self.dino_img = None

        if fruta_img:
            ow, oh = fruta_img.get_size()
            escala = min(ancho_max / ow, alto_max / oh, 1)
            nuevo_w = int(ow * escala)
            nuevo_h = int(oh * escala)
            self.fruta_img = pygame.transform.smoothscale(fruta_img, (nuevo_w, nuevo_h))
        else:
            self.fruta_img = None
            
        # Crear imagen para las estrellas



    def generar_problema(self):
        # Selecciona el problema según el nivel de dificultad usando la función auxiliar
        nivel = self._nivel_from_dificultad(self.dificultad)
        problema, respuesta, operacion = generar_problema_multiplicacion(nivel)
        self.problema_actual = problema
        self.respuesta_correcta = respuesta
        self.operacion_actual = operacion
        self.opciones = self.generar_opciones(self.respuesta_correcta)
        random.shuffle(self.opciones)
        self.tiempo_mensaje = 0
        self.mensaje = ""

    def handle_event(self, evento):
        super().handle_event(evento)
        if evento.type == MOUSEBUTTONDOWN and evento.button == 1:
            for btn in self.opcion_botones:
                if btn.rect.collidepoint(evento.pos):
                    self.jugadas_totales += 1
                    es_correcto = int(btn.texto) == self.respuesta_correcta
                    
                    if es_correcto:
                        self.puntuacion += 1
                        self.racha_correctas += 1
                        self.mejor_racha = max(self.mejor_racha, self.racha_correctas)
                        # Crear efecto de estrellas en la posición del botón
                        self.crear_efecto_estrellas(btn.rect.center)
                        # Crear efecto de partículas en la posición del botón
                        self.crear_explosion_particulas(btn.rect.centerx, btn.rect.centery)
                        # Reproducir sonido si está disponible
                        if self.sounds and "correct" in self.sounds:
                            self.sounds["correct"].play()
                    else:
                        self.racha_correctas = 0
                        if self.sounds and "incorrect" in self.sounds:
                            self.sounds["incorrect"].play()
                    
                    self.mostrar_feedback(es_correcto, self.respuesta_correcta)
                    
                    # Esperar un momento antes de generar el siguiente problema
                    pygame.time.set_timer(pygame.USEREVENT, 1500, True)
                    return
        
        elif evento.type == pygame.USEREVENT:
            self.generar_problema()

    def on_resize(self, ancho, alto):
        """Maneja el redimensionamiento de la ventana"""
        # Recargar imágenes con el nuevo tamaño
        self.cargar_imagenes()
        
        # Actualizar elementos UI
        self.init_responsive_ui()

    def update(self, dt=None):
        if self.tiempo_mensaje > 0:
            self.tiempo_mensaje -= 1
            
        # Actualizar animación de estrellas
        self.update_animacion_estrellas()
        # Actualizar partículas
        self.update_particulas()

    def draw(self, surface):
        self.dibujar_fondo()
        self.mostrar_titulo()

        # Enunciado grande, centrado, debajo del título y arriba de los botones
        enunciado_rect = self.ui_elements["enunciado_rect"]
        enunciado_fuente = obtener_fuente(self.sf(28), negrita=True)
        
        # Dibujar fondo del problema
        dibujar_caja_texto(
            self.pantalla,
            enunciado_rect[0], enunciado_rect[1], 
            enunciado_rect[2], enunciado_rect[3],
            color=(240, 249, 232, 220),
            radius=self.sy(15)
        )
        
        # Dibujar el problema
        self.mostrar_texto(
            self.problema_actual,
            x=enunciado_rect[0],
            y=enunciado_rect[1],
            w=enunciado_rect[2],
            h=enunciado_rect[3],
            fuente=enunciado_fuente,
            color=(30, 30, 30),
            centrado=True
        )

        # Mostrar la operación matemática
        operacion_rect = self.ui_elements["operacion_rect"]
        self.mostrar_operacion(operacion_rect)

        # Opciones de respuesta, debajo del enunciado
        opciones_y = self.ui_elements["opciones_y"]
        self.dibujar_opciones(
            y0=opciones_y,
            estilo="apple",
            border_radius=self.sy(15),
            espacio=self.sx(25)
        )

        # Imagen decorativa (opcional)
        if self.dino_img and self.opcion_botones:
            dino_pos = self.ui_elements["dino_pos"]
            self.pantalla.blit(self.dino_img, dino_pos)

        # Dibujar animación de estrellas
        self.draw_animacion_estrellas()
        # Dibujar partículas
        self.draw_particulas()
        # Feedback
        self.dibujar_feedback()

        # Puntaje
        self.mostrar_puntaje(self.puntuacion, self.jugadas_totales, "Puntaje")
        
        # Mostrar racha actual
        racha_rect = self.ui_elements["racha_rect"]
        self.mostrar_racha(racha_rect)

# Para usar esta clase, crea una instancia pasando los argumentos requeridos por JuegoBase.