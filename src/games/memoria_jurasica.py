import pygame
import random
import os
from .cards import dibujar_carta_generica
from core.juego_base import JuegoBase
from ui.components.utils import Boton  # <-- Importación relativa mejorada

IMG_PATH = os.path.join("assets", "imagenes")
SND_PATH = os.path.join("assets", "sonidos")

def cargar_imagen(nombre, size=None):
    ruta = os.path.join(IMG_PATH, nombre)
    img = pygame.image.load(ruta).convert_alpha()
    if size:
        img = pygame.transform.smoothscale(img, size)
    return img

def cargar_sonido(nombre):
    ruta = os.path.join(SND_PATH, nombre)
    return pygame.mixer.Sound(ruta)

class JuegoMemoriaJurasica(JuegoBase):
    DIFICULTAD_CONFIG = {
        "Fácil":   {"nivel": "Básico",   "pares": 6,  "filas": 3, "columnas": 4},
        "Normal":  {"nivel": "Medio",    "pares": 8,  "filas": 4, "columnas": 4},
        "Difícil": {"nivel": "Avanzado", "pares": 10, "filas": 4, "columnas": 5},
    }

    def __init__(self, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu=None):
        super().__init__('Memoria Jurasica', pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)

        # Colores y fuentes (usa las de JuegoBase si quieres unificar)
        self.color_fondo = (245, 240, 230)
        self.color_titulo = (80, 0, 80)
        self.color_info = (30, 30, 30)

        # Dificultad y nivel
        self.dificultad_seleccionada = dificultad
        self.set_dificultad(dificultad)

        # Recursos gráficos y de sonido
        self.reverso = images.get("card_back") or cargar_imagen("card_back.png", (100, 120))
        self.sonido_acierto = sounds.get("acierto") if sounds else cargar_sonido("acierto.wav")
        self.sonido_error = sounds.get("error") if sounds else cargar_sonido("error.wav")
        self.img_sonido_encendido = images.get("encendido") or cargar_imagen("encendido.png", (40, 40))
        self.img_sonido_apagado = images.get("apagado") or cargar_imagen("apagado.png", (40, 40))
        self.silenciado = False
        self.btn_silencio_rect = None

        # Estado del juego
        self.inicializar_estado()
        self.running = True

    def set_dificultad(self, dificultad):
        config = self.DIFICULTAD_CONFIG.get(dificultad, self.DIFICULTAD_CONFIG["Fácil"])
        self.nivel_actual = config["nivel"]
        self.num_pares = config["pares"]
        self.filas = config["filas"]
        self.columnas = config["columnas"]

    def inicializar_estado(self):
        self.cartas = []
        self.cartas_emparejadas = set()
        self.carta_primera = None
        self.carta_segunda = None
        self.pares_encontrados = 0
        self.total_pares = self.num_pares
        self.nivel_completado = False
        self.carta_rects = []
        self.mostrar_cartas_inicio = True
        self.tiempo_inicio_mostrar = pygame.time.get_ticks()
        self.tiempo_espera = 0
        self.procesando_par = False
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.generar_cartas()

    def cambiar_nivel(self, nueva_dificultad=None):
        if nueva_dificultad and nueva_dificultad in self.DIFICULTAD_CONFIG:
            self.dificultad_seleccionada = nueva_dificultad
        self.set_dificultad(self.dificultad_seleccionada)
        self.inicializar_estado()

    def generar_cartas(self):
        operaciones = self.generar_operaciones(self.nivel_actual, self.num_pares)
        self.cartas = []
        for i, (op, res) in enumerate(operaciones):
            self.cartas.append({
                'id': i,
                'tipo': 'operacion',
                'valor': op,
                'pareja_id': i + self.num_pares,
                'volteada': True,
                'bordes': None
            })
            self.cartas.append({
                'id': i + self.num_pares,
                'tipo': 'resultado',
                'valor': str(res),
                'pareja_id': i,
                'volteada': True,
                'bordes': None
            })
        random.shuffle(self.cartas)

    def generar_operaciones(self, nivel, num_pares):
        operaciones = []
        resultados_usados = set()
        while len(operaciones) < num_pares:
            if nivel == "Básico":
                a, b = random.randint(1, 10), random.randint(1, 10)
                op = f"{a} + {b}"
                res = a + b
            elif nivel == "Medio":
                a, b = random.randint(2, 10), random.randint(2, 10)
                op = f"{a} × {b}"
                res = a * b
            else:  # Avanzado
                tipo = random.choice(['suma', 'resta', 'mult', 'div'])
                if tipo == 'suma':
                    a, b = random.randint(10, 50), random.randint(10, 50)
                    op = f"{a} + {b}"
                    res = a + b
                elif tipo == 'resta':
                    a, b = random.randint(20, 60), random.randint(10, 30)
                    op = f"{a} - {b}"
                    res = a - b
                elif tipo == 'mult':
                    a, b = random.randint(3, 12), random.randint(3, 12)
                    op = f"{a} × {b}"
                    res = a * b
                else:  # División exacta
                    b = random.randint(2, 10)
                    res = random.randint(2, 10)
                    a = b * res
                    op = f"{a} ÷ {b}"
            if res not in resultados_usados:
                resultados_usados.add(res)
                operaciones.append((op, res))
        return operaciones

    def handle_event(self, event):
        # Usa la lógica base para salir y resize
        super().handle_event(event)
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_silencio_rect and self.btn_silencio_rect.collidepoint(event.pos):
                self.silenciado = not self.silenciado
                volumen = 0.0 if self.silenciado else 1.0
                if self.sonido_acierto:
                    self.sonido_acierto.set_volume(volumen)
                if self.sonido_error:
                    self.sonido_error.set_volume(volumen)
                return
            if self.nivel_completado:
                for rect, carta in self.carta_rects:
                    if rect.collidepoint(event.pos) and isinstance(carta, dict) and carta.get('id') == 'siguiente':
                        self.cambiar_nivel()
                        return
            if self.mostrar_cartas_inicio or self.procesando_par or self.nivel_completado:
                return
            for rect, carta in self.carta_rects:
                if rect.collidepoint(event.pos):
                    if carta['id'] in self.cartas_emparejadas or carta.get('volteada'):
                        continue
                    carta['volteada'] = True
                    if not self.carta_primera:
                        self.carta_primera = carta
                    elif not self.carta_segunda and self.carta_primera['id'] != carta['id']:
                        self.carta_segunda = carta
                        self.procesando_par = True
                        self.tiempo_espera = pygame.time.get_ticks()
                    break

    def update(self, dt=0):
        self.actualizar_logica()

    def actualizar_logica(self):
        if self.mostrar_cartas_inicio:
            if pygame.time.get_ticks() - self.tiempo_inicio_mostrar > 1500:
                for carta in self.cartas:
                    if carta['id'] not in self.cartas_emparejadas:
                        carta['volteada'] = False
                self.mostrar_cartas_inicio = False

        if self.procesando_par and self.carta_primera and self.carta_segunda:
            if pygame.time.get_ticks() - self.tiempo_espera > 600:
                if self.carta_primera['pareja_id'] == self.carta_segunda['id']:
                    self.cartas_emparejadas.add(self.carta_primera['id'])
                    self.cartas_emparejadas.add(self.carta_segunda['id'])
                    self.pares_encontrados += 1
                    self.carta_primera['bordes'] = 'acierto'
                    self.carta_segunda['bordes'] = 'acierto'
                    if self.sonido_acierto and not self.silenciado:
                        self.sonido_acierto.play()
                    self.mensaje = "¡Correcto!"
                else:
                    self.carta_primera['bordes'] = 'error'
                    self.carta_segunda['bordes'] = 'error'
                    if self.sonido_error and not self.silenciado:
                        self.sonido_error.play()
                    self.mensaje = "Intenta de nuevo"
                    self.carta_primera['volteada'] = False
                    self.carta_segunda['volteada'] = False
                self.carta_primera = None
                self.carta_segunda = None
                self.procesando_par = False
                self.tiempo_mensaje = pygame.time.get_ticks()
                if self.pares_encontrados >= self.total_pares:
                    self.nivel_completado = True

    def draw(self, surface=None):
        # Mejor uso de métodos base y cuadrícula adaptativa con proporción
        pantalla = surface if surface else self.pantalla
        self.pantalla = pantalla  # Para mantener consistencia interna

        # Fondo y navbar
        self.dibujar_fondo()

        # --- Título y puntaje usando JuegoBase ---
        if hasattr(self, "mostrar_titulo"):
            self.mostrar_titulo()
        if hasattr(self, "pares_encontrados") and hasattr(self, "total_pares"):
            self.mostrar_puntaje(self.pares_encontrados, self.total_pares, "Pares")
        else:
            self.mostrar_puntaje(self.config.get("juegos_ganados", 0), self.config.get("juegos_totales", 0))

        # --- Calcular cuadrícula adaptativa manteniendo proporción ---
        filas, columnas = self.filas, self.columnas
        base_ancho, base_alto = 90, 110
        aspect_ratio = base_ancho / base_alto
        espacio_h, espacio_v = 18, 18

        margen_lateral = 40
        margen_superior = self.navbar_height + 30 + 60 + 10 if hasattr(self, "navbar_height") else 100
        margen_inferior = 80

        area_w = self.pantalla.get_width() - 2 * margen_lateral
        area_h = self.pantalla.get_height() - margen_superior - margen_inferior

        max_card_w = (area_w - (columnas - 1) * espacio_h) / columnas
        max_card_h = (area_h - (filas - 1) * espacio_v) / filas
        if max_card_w / max_card_h > aspect_ratio:
            card_h = int(max_card_h)
            card_w = int(card_h * aspect_ratio)
        else:
            card_w = int(max_card_w)
            card_h = int(card_w / aspect_ratio)
        espacio_h = int(espacio_h * (card_w / base_ancho))
        espacio_v = int(espacio_v * (card_h / base_alto))
        total_ancho = columnas * card_w + (columnas - 1) * espacio_h
        total_alto = filas * card_h + (filas - 1) * espacio_v

        inicio_x = (self.pantalla.get_width() - total_ancho) // 2
        inicio_y = margen_superior + (area_h - total_alto) // 2

        # --- Dibujar cartas ---
        self.carta_rects = []
        for i, carta in enumerate(self.cartas):
            fila = i // columnas
            columna = i % columnas
            x = inicio_x + columna * (card_w + espacio_h)
            y = inicio_y + fila * (card_h + espacio_v)
            rect = dibujar_carta_generica(
                self.pantalla, {**carta, "cartas_emparejadas": self.cartas_emparejadas},
                x, y, card_w, card_h, self.fuente,
                (255, 255, 255), (0, 180, 0), (180, 0, 0), (0, 0, 120),
                self.reverso, (80, 80, 80)
            )
            self.carta_rects.append((rect, carta))

        # --- Mensaje temporal ---
        if self.mensaje and pygame.time.get_ticks() - self.tiempo_mensaje < 1200:
            self.mostrar_texto(
                self.mensaje,
                x=0,
                y=inicio_y - 40,
                w=self.pantalla.get_width(),
                h=30,
                fuente=self.fuente,
                color=(0, 120, 0),
                centrado=True
            )
        elif self.mensaje:
            self.mensaje = ""

        # --- Victoria ---
        if self.nivel_completado:
            self.mostrar_victoria(self.carta_rects)

        # --- Botón de silenciar ---
        img_size = 32
        btn_size = 40
        margin = 12
        x_btn = self.pantalla.get_width() - btn_size - margin
        y_btn = self.pantalla.get_height() - btn_size - margin
        icono = self.img_sonido_apagado if self.silenciado else self.img_sonido_encendido
        if icono.get_width() != img_size or icono.get_height() != img_size:
            icono = pygame.transform.smoothscale(icono, (img_size, img_size))
        btn_silencio = Boton(
            "", x_btn, y_btn, btn_size, btn_size,
            imagen=icono,
            imagen_pos="center",
            estilo="round",
            border_color=(255, 0, 0) if self.silenciado else None,
            border_width=3,
            color_normal=(240, 240, 240),
            color_hover=(255, 220, 220)
        )
        btn_silencio.draw(self.pantalla)
        self.btn_silencio_rect = btn_silencio.rect
