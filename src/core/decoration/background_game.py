import pygame
import random
import math
from collections import deque
from ui.components.utils import get_gradient
from core.scale.responsive_scaler_animated import ResponsiveScalerAnimado  # agregado

PALETA = {
    "azul_cielo": (90, 200, 250),
    "rosa_pastel": (255, 156, 189),
    "verde_lima": (186, 255, 86),
    "lavanda": (186, 156, 255),
    "turquesa": (52, 199, 186)
}

def generar_nube_surface_eficiente(radio_base, color):
    ancho_nube = radio_base * 3.0
    alto_nube = radio_base * 1.8
    surf = pygame.Surface((int(ancho_nube), int(alto_nube)), pygame.SRCALPHA)
    elipses = [
        (radio_base * 1.0, radio_base * 1.0, 1.3, 1.0),
        (radio_base * 1.7, radio_base * 0.8, 1.1, 0.9),
        (radio_base * 0.5, radio_base * 1.1, 1.0, 0.8),
        (radio_base * 1.5, radio_base * 1.3, 1.2, 1.0),
        (radio_base * 2.0, radio_base * 1.1, 1.0, 0.8),
        (radio_base * 1.2, radio_base * 1.5, 1.0, 0.7),
    ]
    for cx, cy, sx, sy in elipses:
        pygame.draw.ellipse(
            surf,
            color,
            pygame.Rect(cx - radio_base * sx / 2, cy - radio_base * sy / 2, radio_base * sx, radio_base * sy)
        )
    pygame.draw.ellipse(
        surf, (255, 255, 255, 60),
        pygame.Rect(radio_base * 0.9, radio_base * 0.5, radio_base * 1.0, radio_base * 0.4)
    )
    return surf.convert_alpha(), (radio_base * 0.7, radio_base * 0.7)

class FondoAnimado:
    def __init__(self, pantalla, navbar_height=0):
        self.pantalla = pantalla
        self.navbar_height = navbar_height

        # dimensiones y escalador animado interno
        self.ANCHO = pantalla.get_width()
        self.ALTO  = pantalla.get_height()
        self.scaler = ResponsiveScalerAnimado(initial_width=self.ANCHO, initial_height=self.ALTO)  # nuevo
        self.sx = self.scaler.sx  # funciones de escalado
        self.sy = self.scaler.sy

        # estado del fondo
        self.burbujas = deque()
        self.nubes    = self._generar_nubes(6)
        self.fondo_actual = None
        self.fondo_cache   = None
        self.tiempo_burbuja = 0

    def set_escaladores(self, sx, sy):
        """Permite inyectar otro sistema de escala (opcional)."""
        self.sx = sx
        self.sy = sy

    def resize(self, ancho, alto):
        """Llamar en VIDEORESIZE: actualiza tamaño, escalador y nubes."""
        self.ANCHO, self.ALTO = ancho, alto
        self.scaler.update(ancho, alto)         # nuevo
        self.fondo_cache = None
        self.nubes = self._generar_nubes(6)

    def _generar_nubes(self, cantidad):
        nubes = []
        for _ in range(cantidad):
            radio = self.sx(60) * random.uniform(1.0, 1.7)
            surf, offset = generar_nube_surface_eficiente(
                radio, (255,255,255, random.randint(90,140))
            )
            nubes.append({
                'x': random.randint(0, self.ANCHO),
                'y': random.randint(self.navbar_height, self.ALTO//3),
                'velocidad': random.uniform(0.15,0.45),
                'surf': surf,
                'offset': offset,
                'w': surf.get_width()
            })
        return nubes

    def update(self):
        """Llamar cada frame antes de draw()."""
        self.scaler.tick()           # nuevo: avanza animación de escala
        self._actualizar_nubes()
        self._actualizar_burbujas()

    def draw(self, fondo=None):
        if fondo != self.fondo_actual or self.fondo_cache is None:
            if isinstance(fondo, pygame.Surface):
                self.fondo_cache = pygame.transform.smoothscale(fondo, (self.ANCHO, self.ALTO))
            elif isinstance(fondo, tuple) and len(fondo) >= 3:
                self.fondo_cache = pygame.Surface((self.ANCHO, self.ALTO))
                self.fondo_cache.fill(fondo)
            else:
                self.fondo_cache = get_gradient(self.ANCHO, self.ALTO, (230, 245, 255), (255, 255, 255))
            self.fondo_actual = fondo

        self.pantalla.blit(self.fondo_cache, (0, 0))
        self._dibujar_nubes()
        self._dibujar_burbujas()

    def _actualizar_nubes(self):
        for nube in self.nubes:
            nube['x'] += nube['velocidad']
            if nube['x'] > self.ANCHO + self.sx(120):
                nube['x'] = -nube['w']
                nube['y'] = random.randint(self.navbar_height, self.ALTO // 3)

    def _dibujar_nubes(self):
        for nube in self.nubes:
            self.pantalla.blit(nube['surf'], (nube['x'] - nube['offset'][0], nube['y'] - nube['offset'][1]))

    def _crear_burbuja(self):
        x = random.randint(self.sx(50), self.ANCHO - self.sx(50))
        y = self.ALTO + self.sy(20)
        color = random.choice(list(PALETA.values()))
        self.burbujas.append({
            'x': x,
            'y': y,
            'radio': random.randint(self.sy(14), self.sy(32)),
            'velocidad': random.uniform(0.4, 1.3),
            'color': (*color[:3], 90),
            'oscilacion': random.uniform(0.7, 1.7),
            'fase': random.uniform(0, 2 * math.pi)
        })

    def _actualizar_burbujas(self):
        self.tiempo_burbuja -= 1
        if self.tiempo_burbuja <= 0:
            self._crear_burbuja()
            self.tiempo_burbuja = random.randint(36, 110)

        ticks = pygame.time.get_ticks()
        self.burbujas = deque([
            dict(b,
                 y=b['y'] - b['velocidad'],
                 x=b['x'] + math.sin(ticks / 520 + b['fase']) * b['oscilacion']
            )
            for b in self.burbujas if b['y'] > -b['radio']
        ])

    def _dibujar_burbujas(self):
        for b in self.burbujas:
            pygame.draw.circle(self.pantalla, b['color'], (int(b['x']), int(b['y'])), b['radio'])
            pygame.draw.circle(
                self.pantalla, (255, 255, 255, 120),
                (int(b['x'] - b['radio'] // 4), int(b['y'] - b['radio'] // 4)),
                b['radio'] // 3
            )
