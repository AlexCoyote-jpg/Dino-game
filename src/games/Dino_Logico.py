import pygame
import random
import math
from pygame.locals import *
from ui.components.utils import mostrar_texto_adaptativo, dibujar_caja_texto, Boton , obtener_fuente
from core.juego_base import JuegoBase , PALETA

class JuegoLogico(JuegoBase):
    # Constantes de clase para reutilizar
    NOMBRES = ["Rexy", "Trici", "Spike", "Dina", "Terry"]
    OBJETOS = ["pasteles", "galletas", "helados", "caramelos"]
    USEREVENT_SIGUIENTE = USEREVENT + 1

    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        super().__init__("Dino Lógico", pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        # --- Carga de imágenes específicas del juego ---
        self.cargar_imagenes()
        # Estado del juego
        self.nivel_actual = self._nivel_from_dificultad(dificultad)
        self.puntuacion = 0
        self.jugadas_totales = 0
        self.racha = 0
        self.tiempo_mensaje = 0
        self.mensaje = ""
        self.problema_actual = ""
        self.respuesta_correcta = None
        self.explicacion = ""
        self.opcion_botones: list[Boton] = []
        self.generar_problema()

    def cargar_imagenes(self):
        """Override: asigna imágenes usadas en draw()"""
        self.dino_img = self.images.get("dino4")
        self.mapa_img = self.images.get("mapa")

    def generar_problema(self):
        if self.nivel_actual == "Básico":
            problema, respuesta, explicacion = self.generar_problema_logico_basico()
        elif self.nivel_actual == "Medio":
            problema, respuesta, explicacion = self.generar_problema_logico_medio()
        else:
            problema, respuesta, explicacion = self.generar_problema_logico_avanzado()
        self.problema_actual = problema
        self.respuesta_correcta = respuesta
        self.explicacion = explicacion
        self.opciones = self.generar_opciones(respuesta)
        random.shuffle(self.opciones)
        self.tiempo_mensaje = 0
        self.mensaje = ""

    def generar_problema_logico_basico(self):
        """Genera 6 problemas básicos de lógica matemática."""
        nombre = random.choice(self.NOMBRES)
        obj = random.choice(self.OBJETOS)
        # Aseguramos que 'n' sea al menos 6 para evitar respuestas negativas
        n = random.randint(6, 15)
        x = random.randint(3, 8)
        y = random.randint(3, 7)
        f = random.randint(20, 40)
        c = random.randint(2, 5)
        lista = [
            (f"{nombre} tiene {n} {obj}. Si da 2 {obj} a cada uno de sus 3 amigos,\n¿Cuántos {obj} le quedarán?",
             n - (2 * 3), f"Multiplica: 2 × 3 = 6, luego resta: {n} - 6 = {n - 6}."),
            (f"{nombre} plantó {x} árboles cada día durante {y} días.\n¿Cuántos árboles plantó en total?",
             x * y, f"Multiplica: {x} × {y} = {x * y}."),
            (f"{nombre} tiene {f} frutas y las repartió en {c} canastas iguales.\n¿Cuántas frutas hay en cada canasta?",
             f // c, f"Divide: {f} ÷ {c} = {f // c}."),
            (f"{nombre} compró {n} cajas de {obj}, cada una con {x} unidades.\n¿Cuántos {obj} compró en total?",
             n * x, f"Multiplica: {n} × {x} = {n * x}."),
            (f"{nombre} tenía {f} caramelos y comió {c} cada día durante {y} días.\n¿Cuántos caramelos le quedan?",
             f - (c * y), f"Multiplica: {c} × {y} = {c * y}, luego resta: {f} - {c * y} = {f - (c * y)}."),
            (f"{nombre} quiere dividir {f} galletas entre {c} amigos.\n¿Cuántas galletas recibirá cada amigo?",
             f // c, f"Divide: {f} ÷ {c} = {f // c}.")
        ]
        return random.choice(lista)

    def generar_problema_logico_medio(self):
        """Genera 6 problemas de dificultad media de lógica matemática."""
        nombre = random.choice(self.NOMBRES)
        a = random.randint(2, 5)
        f = random.randint(5, 15)
        m = random.randint(10, 30)
        d = random.randint(2, 5)
        am = random.randint(3, 8)
        # Para el problema del círculo, forzamos que el total sea par
        total = random.randint(3, 7) * 2  
        # Usamos etiquetas de 1 a total para mayor claridad
        pos = random.randint(1, total)
        lista = [
            (f"{nombre} y sus {a} amigos fueron a recoger frutas. Cada uno recogió {f} frutas.\n¿Cuántas frutas recogieron en total?",
             f * (a + 1), f"Multiplica: {f} × {a + 1} = {f * (a + 1)}."),
            (f"{nombre} tiene {m} monedas. Si da {d} monedas a cada amigo y tiene {am} amigos,\n¿Cuántas monedas le quedarán?",
             m - (d * am), f"Multiplica: {d} × {am} = {d * am}, luego resta: {m} - {d * am} = {m - (d * am)}."),
            (f"{nombre} y sus amigos están formados en un círculo. Si hay {total} dinosaurios en total y {nombre} es el número {pos},\n¿Cuál es el número del dinosaurio que está frente a {nombre}?",
             (pos + total//2 - 1) % total + 1,
             f"Suma la mitad de {total} a {pos}, resta 1, aplica módulo {total} y suma 1."),
            (f"{nombre} tiene {m} caramelos y quiere repartirlos en bolsas de {d} caramelos cada una.\n¿Cuántas bolsas puede llenar completamente?",
             m // d, f"Divide: {m} ÷ {d} = {m // d}."),
            (f"{nombre} compró {a} cajas de {f} galletas cada una. Luego regaló {d} galletas.\n¿Cuántas galletas le quedan?",
             (a * f) - d, f"Multiplica: {a} × {f} = {a * f}, luego resta: {a * f} - {d} = {(a * f) - d}."),
            (f"{nombre} tiene {total} amigos y quiere darles {pos} caramelos a cada uno.\n¿Cuántos caramelos necesita en total?",
             total * pos, f"Multiplica: {total} × {pos} = {total * pos}.")
        ]
        return random.choice(lista)

    def generar_problema_logico_avanzado(self):
        """Genera 6 problemas avanzados de lógica matemática."""
        nombre = random.choice(self.NOMBRES)
        a = random.randint(3, 6)
        p = random.randint(2, 3)
        l = random.randint(5, 10)
        # Para el problema del círculo, forzamos que el total sea par
        total = random.randint(3, 7) * 2  
        salto = random.randint(2, 3)
        m = random.randint(20, 40)
        s = random.randint(4, 8)
        lista = [
            (f"{nombre} organiza una carrera con {a} amigos. Si cada uno corre a una velocidad diferente y {nombre} llega en la posición {p},\n¿Cuántos dinosaurios llegaron después de él?",
             a - p + 1, f"Resta la posición de {nombre} a los participantes: {a} - {p} + 1 = {a - p + 1}."),
            (f"{nombre} tiene un jardín cuadrado con {l} metros por lado. Quiere plantar flores en el borde, poniendo una flor cada metro.\n¿Cuántas flores necesitará?",
             l * 4, f"El perímetro es 4 × {l} = {l * 4}."),
            (f"{nombre} y sus amigos están jugando a pasarse una pelota. Son {total} dinosaurios en total, formados en círculo. Si cada uno pasa la pelota al dinosaurio que está {salto} posiciones a su derecha,\n¿Cuántos pases se necesitan para que la pelota vuelva al dinosaurio que la lanzó primero?",
             total // math.gcd(total, salto),
             f"El mínimo número de pases es {total} dividido por el MCD de {total} y {salto}."),
            (f"{nombre} tiene {m} monedas y quiere repartirlas en sobres de {s} monedas cada uno.\n¿Cuántos sobres puede llenar completamente?",
             m // s, f"Divide: {m} ÷ {s} = {m // s}."),
            (f"{nombre} quiere construir una cerca alrededor de un terreno rectangular de {l} metros de largo y {p} metros de ancho.\n¿Cuántos metros de cerca necesita?",
             2 * (l + p), f"El perímetro es 2 × ({l} + {p}) = {2 * (l + p)}."),
            (f"{nombre} tiene {m} caramelos y quiere repartirlos entre {s} amigos de forma equitativa.\n¿Cuántos caramelos recibirá cada uno?",
             m // s, f"Divide: {m} ÷ {s} = {m // s}.")
        ]
        return random.choice(lista)

    def handle_event(self, evento):
        super().handle_event(evento)
        if evento.type == MOUSEBUTTONDOWN and evento.button == 1:
            for btn in self.opcion_botones:
                if btn.rect.collidepoint(evento.pos):
                    self.jugadas_totales += 1
                    es_correcto = int(btn.texto) == self.respuesta_correcta
                    if es_correcto:
                        self.puntuacion += 1
                        self.racha += 1
                        # Efecto de partículas en el centro del botón correcto
                        self.crear_explosion_particulas(btn.rect.centerx, btn.rect.centery)
                    else:
                        self.racha = 0
                    self.mostrar_feedback(es_correcto, self.respuesta_correcta)
                    self.tiempo_mensaje = 90
                    pygame.time.set_timer(self.USEREVENT_SIGUIENTE, 900, True)
                    return
        elif evento.type == self.USEREVENT_SIGUIENTE:
            self.generar_problema()

    def update(self, dt=None):
        if self.tiempo_mensaje > 0:
            self.tiempo_mensaje -= 1
        self.update_animacion_estrellas()
        self.update_particulas()

    def draw(self, surface):
        self.dibujar_fondo()
        self.mostrar_titulo()

        # Precompute common scaling values
        margin_left = self.sx(50)
        gap = self.sx(30)
        nav_offset = self.sy(100)
        content_y = self.navbar_height + nav_offset

        # Dibujar imagen de dinosaurio (si existe)
        dino_width = 0
        if self.dino_img:
            dino_width = int(self.ANCHO * 0.15)
            ow, oh = self.dino_img.get_size()
            dino_height = int(oh * dino_width / ow)
            dino_scaled = pygame.transform.smoothscale(self.dino_img, (dino_width, dino_height))
            self.pantalla.blit(dino_scaled, (margin_left, content_y))

        # Dibujar caja de problema a la derecha de la imagen de dino
        text_x = margin_left + dino_width + gap
        text_y = content_y
        text_w = self.ANCHO - text_x - margin_left
        text_h = max(self.sy(100), int(self.ALTO * 0.15))
        dibujar_caja_texto(
            self.pantalla,
            text_x, text_y,
            text_w, text_h,
            color=(255, 255, 240, 230),
            radius=self.sx(20)
        )
        enunciado_fuente = obtener_fuente(max(self.sf(40), int(self.ALTO * 0.05)), negrita=True)
        self.mostrar_texto(
            self.problema_actual,
            x=text_x,
            y=text_y,
            w=text_w,
            h=text_h,
            fuente=enunciado_fuente,
            color=(30, 30, 30),
            centrado=True
        )

        # Dibujar las opciones de respuesta
        opciones_y = text_y + text_h + self.sy(40)
        self.dibujar_opciones(y0=opciones_y)

        # Dibujar feedback y animaciones adicionales
        self.dibujar_feedback()
        self.draw_animacion_estrellas()
        self.draw_particulas()

        # Mostrar puntaje
        self.mostrar_puntaje(self.puntuacion, self.jugadas_totales, "Puntaje")

        # Dibujar el mapa en la esquina inferior derecha, justo arriba de la racha
        if self.mapa_img:
            map_width = int(self.ANCHO * 0.15)
            ow, oh = self.mapa_img.get_size()
            map_height = int(oh * map_width / ow)
            map_x = self.ANCHO - map_width - self.sx(20)
            map_y = self.ALTO - map_height - self.sy(100)
            self.pantalla.blit(
                pygame.transform.smoothscale(self.mapa_img, (map_width, map_height)),
                (map_x, map_y)
            )

        # Mostrar la racha
        self.mostrar_racha()



