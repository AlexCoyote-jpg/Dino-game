"""
Módulo para lógica de fondo animado y gestión de estrellas.
"""
import pygame
import random
import math
from collections import defaultdict

class FondoAnimado:
    """
    Fondo animado con gradiente y estrellas que se mueven y parpadean.
    Eficiente y adaptable a cualquier tamaño.
    """
    def __init__(self, ancho, alto, color_fondo1=(255, 250, 240), color_fondo2=(255, 235, 205), max_estrellas=20):
        self.color_fondo1 = color_fondo1
        self.color_fondo2 = color_fondo2
        self.max_estrellas = max_estrellas
        self.resize(ancho, alto)

    def resize(self, ancho, alto):
        self.ancho, self.alto = ancho, alto
        self.fondo = pygame.Surface((ancho, alto))
        dibujar_gradiente(self.fondo, self.color_fondo1, self.color_fondo2)
        self.estrellas = crear_estrellas_pantalla(ancho, alto, self.max_estrellas)

    def update(self, dt=1.0):
        for estrella in self.estrellas:
            estrella.update(self.ancho, self.alto, dt)

    def draw(self, surface):
        surface.blit(self.fondo, (0, 0))
        for estrella in self.estrellas:
            estrella.draw(surface)

# --- Funciones utilitarias ---
def dibujar_gradiente(surf, color1, color2):
    width, height = surf.get_size()
    for y in range(height):
        ratio = y / (height - 1)
        color = tuple(int(color1[i] + (color2[i] - color1[i]) * ratio) for i in range(3))
        pygame.draw.line(surf, color, (0, y), (width, y))

def crear_estrellas_pantalla(ancho, alto, max_estrellas):
    area = ancho * alto
    num_estrellas = min(max(area // 30000, 6), max_estrellas)
    cell_size = 48
    grid = defaultdict(list)
    estrellas = []
    intentos = 0
    while len(estrellas) < num_estrellas and intentos < num_estrellas * 30:
        nueva = Estrella(ancho, alto)
        cx, cy = int(nueva.x // cell_size), int(nueva.y // cell_size)
        if all(not nueva.colisiona_con(e) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for e in grid[(cx+dx, cy+dy)]):
            estrellas.append(nueva)
            grid[(cx, cy)].append(nueva)
        intentos += 1
    return estrellas

class Estrella:
    def __init__(self, ancho, alto):
        self.radio_base = random.randint(16, 32)
        self.x = random.uniform(self.radio_base, ancho - self.radio_base)
        self.y = random.uniform(self.radio_base, alto - self.radio_base)
        self.color = random.choice([(255, 255, 255), (255, 255, 200), (255, 240, 180), (255, 235, 255)])
        self.puntos = random.choice([5, 6, 7])
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(20, 80) / 60.0
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.fase = random.uniform(0, 2 * math.pi)
        self.parpadeo_vel = random.uniform(1.5, 2.5)
        self.radio = self.radio_base

    def update(self, ancho, alto, dt=1.0):
        self.x += self.dx * dt
        self.y += self.dy * dt
        if not (self.radio < self.x < ancho - self.radio): self.dx *= -1
        if not (self.radio < self.y < alto - self.radio): self.dy *= -1
        self.fase += self.parpadeo_vel * 0.03 * dt
        self.radio = int(self.radio_base * (0.85 + 0.15 * math.sin(self.fase)))

    def draw(self, surface):
        dibujar_estrella(surface, self.color, (int(self.x), int(self.y)), self.radio, self.puntos)

    def colisiona_con(self, otra):
        return math.hypot(self.x - otra.x, self.y - otra.y) < (self.radio + otra.radio)

def dibujar_estrella(surface, color, center, radius, points):
    angle = math.pi / points
    vertices = [
        (
            center[0] + int((radius if i % 2 == 0 else radius // 2) * math.sin(i * angle)),
            center[1] - int((radius if i % 2 == 0 else radius // 2) * math.cos(i * angle))
        ) for i in range(2 * points)
    ]
    pygame.draw.polygon(surface, color, vertices)

# --- API retrocompatible ---
crear_fondo = lambda w, h, c1=(255, 250, 240), c2=(255, 235, 205): dibujar_gradiente(pygame.Surface((w, h)), c1, c2)
crear_estrellas = crear_estrellas_pantalla
actualizar_estrellas = lambda estrellas, w, h: [e.update(w, h) for e in estrellas] or estrellas
