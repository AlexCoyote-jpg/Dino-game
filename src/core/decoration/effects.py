import pygame
import random
import math
import time
from ui.components.utils import get_gradient, mostrar_texto_adaptativo, obtener_fuente
from ui.components.emoji import mostrar_alternativo_adaptativo

# Mensajes de feedback
mensajes_correcto = [
    "¡Excelente! 🦕✨",
    "¡Muy bien! ¡Dino está feliz! 🥚🎉",
    "¡Correcto! ¡Sigue así! 🌟",
    "¡Genial! ¡Eres un crack! 🦖",
    "¡Perfecto! ¡Continúa así! 🔥",
    "¡Increíble respuesta! 🌈",
    "¡Eso es! ¡Dino está impresionado! 🦖👏",
    "¡Fantástico trabajo! ⭐⭐⭐",
    "¡Súper! ¡Lo lograste! 🎯",
    "¡Maravilloso! ¡Sigue así! 🎊"
]

mensajes_incorrecto = [
    "¡Ups! Intenta de nuevo, tú puedes 🦕",
    "¡No te rindas! La respuesta era {respuesta} 🥚",
    "¡Casi! Sigue practicando 💪",
    "¡Ánimo! Dino confía en ti 🦖",
    "¡Inténtalo otra vez! Estás cerca 🔍",
    "¡No pasa nada! Aprendemos de los errores 📚",
    "¡Vamos! La próxima lo conseguirás 🎯",
    "¡Sigue intentando! Dino te apoya 🦕❤️",
    "¡Oops! Prueba de nuevo 🌟",
    "¡Casi lo tienes! Sigue intentando 🌈"
]

PALETA = {
    "rojo_manzana": (255, 59, 48),
    "naranja_zanahoria": (255, 149, 0),
    "amarillo_sol": (255, 204, 0),
    "verde_manzana": (76, 217, 100),
    "verde_lima": (186, 255, 86),
    "azul_cielo": (90, 200, 250),
    "azul_oceano": (0, 122, 255),
    "morado_uva": (175, 82, 222),
    "rosa_chicle": (255, 45, 85),
    "rosa_pastel": (255, 156, 189),
    "turquesa": (52, 199, 186),
    "coral": (255, 127, 80),
    "lavanda": (186, 156, 255),
    "melocoton": (255, 190, 152),
    "menta": (152, 255, 179)
}

class EffectsMixin:
    def mostrar_feedback(self, es_correcto, respuesta_correcta=None):
        if es_correcto:
            mensaje = random.choice(mensajes_correcto)
            self.racha_correctas += 1
            self.mejor_racha = max(self.mejor_racha, self.racha_correctas)
            self.tiempo_cambio_racha = time.time()
            self.mensaje_color = (152, 251, 152, 220)
            self.crear_efecto_estrellas((self.ANCHO // 2, self.ALTO // 2))
            if self.sonido_activado and 'correcto' in self.sounds:
                self.sounds['correcto'].play()
        else:
            mensaje = random.choice(mensajes_incorrecto)
            if respuesta_correcta is not None:
                mensaje = mensaje.format(respuesta=respuesta_correcta)
            self.racha_correctas = 0
            self.mensaje_color = (255, 182, 193, 220)
            if self.sonido_activado and 'incorrecto' in self.sounds:
                self.sounds['incorrecto'].play()
        self.mostrar_mensaje_temporal(mensaje)

    def mostrar_mensaje_temporal(self, mensaje, tiempo=60, color=None):
        self.mensaje = mensaje
        self.tiempo_mensaje = tiempo
        if color:
            self.mensaje_color = color
        self.mensaje_animacion = 1.0

    def dibujar_feedback(self):
        if self.tiempo_mensaje > 0 and self.mensaje:
            ancho = self.sx(550)
            alto = self.sy(80)
            x = (self.ANCHO - ancho) // 2
            y = self.ALTO - self.sy(180)
            if y < self.navbar_height:
                y = self.navbar_height + self.sy(10)
            if self.tiempo_mensaje < 10:
                factor = self.tiempo_mensaje / 10
                alto = int(alto * factor)
                self.mensaje_animacion = factor
            elif self.mensaje_animacion < 1.0:
                self.mensaje_animacion = min(1.0, self.mensaje_animacion + 0.1)
                alto = int(alto * self.mensaje_animacion)
            surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            sombra = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            pygame.draw.rect(
                sombra,
                (0, 0, 0, 40),
                (4, 4, ancho, alto),
                border_radius=self.sy(25)
            )
            surf.blit(sombra, (0, 0))
            pygame.draw.rect(
                surf,
                (255, 255, 255, 240),
                (0, 0, ancho, alto),
                border_radius=self.sy(25)
            )
            gradiente = get_gradient(ancho, alto, 
                                    self.mensaje_color[:3], 
                                    tuple(max(0, c-30) for c in self.mensaje_color[:3]))
            gradiente.set_alpha(self.mensaje_color[3] if len(self.mensaje_color) > 3 else 180)
            mask = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            pygame.draw.rect(
                mask,
                (255, 255, 255, 255),
                (0, 0, ancho, alto),
                border_radius=self.sy(25)
            )
            gradiente_masked = gradiente.copy()
            gradiente_masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(gradiente_masked, (0, 0))
            pygame.draw.rect(
                surf,
                (255, 255, 255, 150),
                (0, 0, ancho, alto),
                width=3,
                border_radius=self.sy(25)
            )
            self.pantalla.blit(surf, (x, y))
            sombra_offset = self.sy(2)
            mostrar_texto_adaptativo(
                self.pantalla,
                self.mensaje,
                x + sombra_offset, y + sombra_offset,
                ancho, alto,
                fuente_base=self.fuente,
                color=(10, 10, 10, 150),
                centrado=True
            )
            mostrar_texto_adaptativo(
                self.pantalla,
                self.mensaje,
                x, y,
                ancho, alto,
                fuente_base=self.fuente,
                color=(30, 30, 30),
                centrado=True
            )
            self.tiempo_mensaje -= 1

    def crear_estrella_img(self, tamaño=None, color=(255, 215, 0)):
        tamaño = tamaño or self.sy(20)
        img = pygame.Surface((tamaño, tamaño), pygame.SRCALPHA)
        puntos = []
        for i in range(5):
            ang = math.pi/2 + i * 2*math.pi/5
            puntos.append((
                tamaño//2 + int(tamaño//2 * math.cos(ang)),
                tamaño//2 - int(tamaño//2 * math.sin(ang))
            ))
            ang += math.pi/5
            puntos.append((
                tamaño//2 + int(tamaño//5 * math.cos(ang)),
                tamaño//2 - int(tamaño//5 * math.sin(ang))
            ))
        pygame.draw.polygon(img, color, puntos)
        return img

    def crear_estrella_img_simple(self, tamaño=None, color=(255, 215, 0)):
        """
        Crea una imagen de estrella simple para efectos de celebración.
        Este método replica el efecto clásico de estrella usado en dino_cazador.
        """
        tamaño = tamaño or self.sy(15)
        img = pygame.Surface((tamaño, tamaño), pygame.SRCALPHA)
        puntos = []
        for i in range(5):
            ang = math.pi/2 + i * 2*math.pi/5
            puntos.append((
                tamaño//2 + int(tamaño//2 * math.cos(ang)),
                tamaño//2 - int(tamaño//2 * math.sin(ang))
            ))
            ang += math.pi/5
            puntos.append((
                tamaño//2 + int(tamaño//5 * math.cos(ang)),
                tamaño//2 - int(tamaño//5 * math.sin(ang))
            ))
        pygame.draw.polygon(img, color, puntos)
        return img

    def crear_efecto_estrellas(self, posicion, cantidad=12, colores=None):
        x, y = posicion
        if not hasattr(self, 'estrella_img') or self.estrella_img is None:
            self.estrella_img = self.crear_estrella_img()
        if colores is None:
            colores = [
                PALETA["amarillo_sol"],
                PALETA["rosa_chicle"],
                PALETA["verde_lima"],
                PALETA["azul_cielo"],
                PALETA["naranja_zanahoria"]
            ]
        for _ in range(cantidad):
            angulo = random.uniform(0, 2 * math.pi)
            distancia = random.uniform(self.sy(30), self.sy(150))
            estrella_x = x + math.cos(angulo) * distancia
            estrella_y = y + math.sin(angulo) * distancia
            escala = random.uniform(0.8, 1.8)
            rotacion = random.uniform(0, 360)
            vida = random.randint(60, 100)
            velocidad_x = math.cos(angulo) * random.uniform(0.8, 2.5)
            velocidad_y = math.sin(angulo) * random.uniform(0.8, 2.5) - random.uniform(0.8, 2.0)
            color = random.choice(colores)
            if not hasattr(self, 'estrellas'):
                self.estrellas = []
            self.estrellas.append({
                'x': estrella_x, 'y': estrella_y,
                'escala': escala, 'rotacion': rotacion,
                'vida': vida, 'max_vida': vida,
                'vel_x': velocidad_x, 'vel_y': velocidad_y,
                'color': color
            })
        self.animacion_activa = True
        self.tiempo_animacion = 120
        if self.sonido_activado and 'estrella' in self.sounds:
            self.sounds['estrella'].play()

    def crear_efecto_estrellas_simple(self, posicion, cantidad=5):
        """
        Crea estrellas para celebrar una respuesta correcta (versión simple).
        """
        x, y = posicion
        if not hasattr(self, 'estrella_img_simple') or self.estrella_img_simple is None:
            self.estrella_img_simple = self.crear_estrella_img_simple()
        if not hasattr(self, 'estrellas_simple'):
            self.estrellas_simple = []
        for _ in range(cantidad):
            angulo = random.uniform(0, 2 * math.pi)
            distancia = random.uniform(self.sy(30), self.sy(100))
            estrella_x = x + math.cos(angulo) * distancia
            estrella_y = y + math.sin(angulo) * distancia
            escala = random.uniform(0.7, 1.3)
            rotacion = random.uniform(0, 360)
            vida = random.randint(40, 80)
            self.estrellas_simple.append({
                'x': estrella_x, 'y': estrella_y,
                'escala': escala, 'rotacion': rotacion,
                'vida': vida, 'max_vida': vida
            })
        self.animacion_activa_simple = True
        self.tiempo_animacion_simple = 60

    def crear_particula(self, x, y, color=None, velocidad=None, tamaño=None, vida=None, forma="circulo"):
        if color is None:
            color = random.choice(list(PALETA.values()))
        if velocidad is None:
            angulo = random.uniform(0, 2 * math.pi)
            magnitud = random.uniform(0.8, 3.0)
            velocidad = (math.cos(angulo) * magnitud, math.sin(angulo) * magnitud)
        if tamaño is None:
            tamaño = random.uniform(self.sy(5), self.sy(12))
        if vida is None:
            vida = random.randint(30, 70)
        if not hasattr(self, 'particulas'):
            self.particulas = []
        self.particulas.append({
            'x': x, 'y': y,
            'vel_x': velocidad[0], 'vel_y': velocidad[1],
            'tamaño': tamaño, 'tamaño_original': tamaño,
            'color': color, 'vida': vida, 'max_vida': vida,
            'forma': forma
        })

    def crear_explosion_particulas(self, x, y, cantidad=30, colores=None, radio=None):
        if colores is None:
            colores = random.sample(list(PALETA.values()), min(6, len(PALETA)))
        if radio is None:
            radio = self.sy(120)
        formas = ["circulo", "cuadrado", "triangulo", "estrella", "corazon"]
        if not hasattr(self, 'particulas'):
            self.particulas = []
        for _ in range(cantidad):
            angulo = random.uniform(0, 2 * math.pi)
            magnitud = random.uniform(1.5, 4.0)
            vel_x = math.cos(angulo) * magnitud
            vel_y = math.sin(angulo) * magnitud
            tamaño = random.uniform(self.sy(6), self.sy(15))
            color = random.choice(colores)
            vida = random.randint(40, 80)
            forma = random.choice(formas)
            self.particulas.append({
                'x': x, 'y': y,
                'vel_x': vel_x, 'vel_y': vel_y,
                'tamaño': tamaño, 'tamaño_original': tamaño,
                'color': color, 'vida': vida, 'max_vida': vida,
                'forma': forma
            })
        if self.sonido_activado and 'explosion' in self.sounds:
            self.sounds['explosion'].play()

    def update_animacion_estrellas(self):
        if not hasattr(self, 'estrellas'):
            self.estrellas = []
        for s in self.estrellas[:]:
            s['rotacion'] += 3
            s['vida'] -= 1
            s['vel_y'] += 0.05
            s['x'] += s['vel_x']
            s['y'] += s['vel_y']
            if s['vida'] < s['max_vida'] * 0.3:
                s['escala'] *= 0.97
            if s['vida'] <= 0:
                self.estrellas.remove(s)
        if hasattr(self, 'animacion_activa') and self.animacion_activa:
            self.tiempo_animacion -= 1
            if self.tiempo_animacion <= 0:
                self.animacion_activa = False

    def update_animacion_estrellas_simple(self):
        """
        Actualiza la animación de las estrellas simples.
        """
        if not hasattr(self, 'estrellas_simple'):
            self.estrellas_simple = []
        for s in self.estrellas_simple[:]:
            s['rotacion'] += 2
            s['vida'] -= 1
            if s['vida'] <= 0:
                self.estrellas_simple.remove(s)
        if hasattr(self, 'animacion_activa_simple') and self.animacion_activa_simple:
            self.tiempo_animacion_simple -= 1
            if self.tiempo_animacion_simple <= 0:
                self.animacion_activa_simple = False

    def update_particulas(self):
        if not hasattr(self, 'particulas'):
            self.particulas = []
        for p in self.particulas[:]:
            p['vida'] -= 1
            p['x'] += p['vel_x']
            p['y'] += p['vel_y']
            p['vel_y'] += 0.1
            p['vel_x'] *= 0.98
            factor_vida = p['vida'] / p['max_vida']
            p['tamaño'] = p['tamaño_original'] * max(0.2, factor_vida)
            if p['vida'] <= 0:
                self.particulas.remove(p)

    def draw_animacion_estrellas(self):
        if not hasattr(self, 'estrella_img') or self.estrella_img is None:
            self.estrella_img = self.crear_estrella_img()
        if not hasattr(self, 'estrellas'):
            self.estrellas = []
        for s in self.estrellas:
            opacidad = int(255 * (s['vida'] / s['max_vida']))
            estrella_coloreada = self.crear_estrella_img(
                tamaño=int(self.sy(20) * s['escala']),
                color=s['color']
            )
            img_rotada = pygame.transform.rotozoom(
                estrella_coloreada,
                s['rotacion'],
                1.0
            )
            img_rotada.set_alpha(opacidad)
            if opacidad > 150:
                glow = pygame.transform.rotozoom(img_rotada, 0, 1.5)
                glow.set_alpha(opacidad // 3)
                glow_rect = glow.get_rect(center=(s['x'], s['y']))
                self.pantalla.blit(glow, glow_rect)
            rect = img_rotada.get_rect(center=(s['x'], s['y']))
            self.pantalla.blit(img_rotada, rect)

    def draw_animacion_estrellas_simple(self):
        """
        Dibuja las estrellas animadas simples.
        """
        if not hasattr(self, 'estrella_img_simple') or self.estrella_img_simple is None:
            self.estrella_img_simple = self.crear_estrella_img_simple()
        if not hasattr(self, 'estrellas_simple'):
            self.estrellas_simple = []
        for s in self.estrellas_simple:
            opacidad = int(255 * (s['vida'] / s['max_vida']))
            img_rotada = pygame.transform.rotozoom(
                self.estrella_img_simple,
                s['rotacion'],
                s['escala']
            )
            img_rotada.set_alpha(opacidad)
            rect = img_rotada.get_rect(center=(s['x'], s['y']))
            self.pantalla.blit(img_rotada, rect)

    def draw_particulas(self):
        if not hasattr(self, 'particulas'):
            self.particulas = []
        for p in self.particulas:
            opacidad = int(255 * (p['vida'] / p['max_vida']))
            color = (*p['color'][:3], opacidad)
            tamaño = int(p['tamaño'])
            if tamaño <= 0:
                continue
            surf = pygame.Surface((tamaño*2, tamaño*2), pygame.SRCALPHA)
            if p['forma'] == "circulo":
                pygame.draw.circle(surf, color, (tamaño, tamaño), tamaño)
            elif p['forma'] == "cuadrado":
                pygame.draw.rect(surf, color, (0, 0, tamaño*2, tamaño*2), border_radius=tamaño//3)
            elif p['forma'] == "triangulo":
                pygame.draw.polygon(surf, color, [
                    (tamaño, 0),
                    (0, tamaño*2),
                    (tamaño*2, tamaño*2)
                ])
            elif p['forma'] == "estrella":
                puntos = []
                for i in range(5):
                    ang = math.pi/2 + i * 2*math.pi/5
                    puntos.append((
                        tamaño + int(tamaño * 0.8 * math.cos(ang)),
                        tamaño - int(tamaño * 0.8 * math.sin(ang))
                    ))
                    ang += math.pi/5
                    puntos.append((
                        tamaño + int(tamaño * 0.3 * math.cos(ang)),
                        tamaño - int(tamaño * 0.3 * math.sin(ang))
                    ))
                pygame.draw.polygon(surf, color, puntos)
            elif p['forma'] == "corazon":
                radio = tamaño * 0.8
                pygame.draw.circle(surf, color, (tamaño - int(radio//2), tamaño - int(radio//2)), int(radio//2))
                pygame.draw.circle(surf, color, (tamaño + int(radio//2), tamaño - int(radio//2)), int(radio//2))
                pygame.draw.polygon(surf, color, [
                    (tamaño - radio, tamaño - radio//3),
                    (tamaño + radio, tamaño - radio//3),
                    (tamaño, tamaño + radio)
                ])
            self.pantalla.blit(surf, (p['x'] - tamaño, p['y'] - tamaño))