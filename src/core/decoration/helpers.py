import random
import pygame
from ui.components.utils import mostrar_texto_adaptativo, dibujar_caja_texto, obtener_fuente
from ui.components.emoji import mostrar_alternativo_adaptativo
from ui.components.utils import Boton

def mostrar_texto(pantalla, texto, x, y, w, h, fuente, color=(30,30,30), centrado=False):
    """Muestra texto adaptativo en pantalla con coordenadas escaladas."""
    mostrar_texto_adaptativo(
        pantalla=pantalla,
        texto=texto,
        x=x,
        y=y,
        w=w,
        h=h,
        fuente_base=fuente,
        color=color,
        centrado=centrado
    )

def mostrar_titulo(pantalla, nombre, dificultad, fuente_titulo, ui_elements, navbar_height, sy, ANCHO):
    """Muestra el título del juego centrado debajo de la navbar."""
    titulo_rect = ui_elements.get("titulo_rect", 
                                 (0, navbar_height + sy(30), 
                                  ANCHO, sy(60)))
    mostrar_texto_adaptativo(
        pantalla=pantalla,
        texto=f"{nombre} - Nivel {dificultad}",
        x=titulo_rect[0],
        y=titulo_rect[1],
        w=titulo_rect[2],
        h=titulo_rect[3],
        fuente_base=fuente_titulo,
        color=(70, 130, 180),
        centrado=True
    )
def mostrar_instrucciones(pantalla, sx, sy, ALTO, ANCHO, fuente_pequeña, texto=None):
    instrucciones_rect = (
        sx(50),
        ALTO - sy(70),
        ANCHO - sx(100),
        sy(50)
    )
    mostrar_texto_adaptativo(
        pantalla=pantalla,
        texto=texto or "Selecciona la opción correcta. Presiona ESC para volver.",
        x=instrucciones_rect[0],
        y=instrucciones_rect[1],
        w=instrucciones_rect[2],
        h=instrucciones_rect[3],
        fuente_base=fuente_pequeña,
        color=(100, 100, 100),
        centrado=True
    )    

def mostrar_puntaje(pantalla, juegos_ganados, juegos_totales, fuente, sy, sx, ALTO, ui_elements, frase="¡Puntaje!"):
    """Muestra el puntaje en la parte inferior izquierda en una caja bonita con emojis."""
    puntaje_rect = ui_elements.get("puntaje_rect", 
                                   (sx(18), ALTO - sy(48) - sy(18), 
                                    sx(180), sy(48)))
    x, y, ancho_caja, alto_caja = puntaje_rect
    texto = f"🏆 {frase}: {juegos_ganados}/{juegos_totales} 🎮"
    dibujar_caja_texto(
        pantalla,
        x, y, ancho_caja, alto_caja,
        color=(240, 250, 255, 230),
        radius=sy(18),
        texto=texto,
        fuente=fuente,
        color_texto=(30, 60, 90)
    )

@staticmethod
def color_complementario(rgb):
    return tuple(255 - c for c in rgb)

def dibujar_opciones(
    pantalla, opciones, fuente, sx, sy, ANCHO, ALTO, PALETA, opcion_botones,
    tooltips=None, estilo="flat", border_radius=None, x0=None, y0=None, espacio=None, tooltip_manager=None
):
    """Dibuja botones de opciones de forma responsiva, colorida y reutilizable."""
    if not opciones:
        return
    border_radius = border_radius or sy(12)
    espacio = espacio or sx(20)
    cnt = len(opciones)
    w = max(sx(100), min(sx(180), ANCHO // (cnt * 2)))
    h = max(sy(50), min(sy(80), ALTO // 12))
    if x0 is None:
        x0 = (ANCHO - (w * cnt + espacio * (cnt - 1))) // 2
    if y0 is None:
        y0 = ALTO // 2 - h // 2
    paleta = PALETA[:cnt] if cnt <= len(PALETA) else PALETA * (cnt // len(PALETA)) + PALETA[:cnt % len(PALETA)]
    opcion_botones.clear()
    for i, val in enumerate(opciones):
        color_bg = paleta[i % len(paleta)]
        color_hover = color_complementario(color_bg)
        lum = 0.299 * color_bg[0] + 0.587 * color_bg[1] + 0.114 * color_bg[2]
        color_texto = (0, 0, 0) if lum > 180 else (255, 255, 255)
        x = x0 + i * (w + espacio)
        btn = Boton(
            texto=str(val),
            x=x, y=y0, ancho=w, alto=h,
            fuente=fuente,
            color_normal=color_bg,
            color_hover=color_hover,
            color_texto=color_texto,
            border_radius=border_radius,
            estilo=estilo,
            tooltip=tooltips[i] if tooltips and i < len(tooltips) else None
        )
        btn.draw(pantalla, tooltip_manager=tooltip_manager)
        opcion_botones.append(btn)

def mostrar_victoria(
    pantalla, sx, sy, ANCHO, ALTO, fuente_titulo, fuente, mostrar_alternativo_adaptativo,
    mostrar_texto_adaptativo, Boton, dibujar_caja_texto, carta_rects, color_panel=(255, 255, 224), color_borde=(255, 215, 0)
):
    """Muestra pantalla de victoria con escalado responsivo."""
    ancho_panel = sx(500)
    alto_panel = sy(200)
    x_panel = (ANCHO - ancho_panel) // 2
    y_panel = (ALTO - alto_panel) // 2
    panel = pygame.Surface((ancho_panel, alto_panel), pygame.SRCALPHA)
    for i in range(alto_panel):
        factor = i / alto_panel
        r = int(255 - factor * 50)
        g = int(250 - factor * 20)
        b = int(150 + factor * 50)
        pygame.draw.line(panel, (r, g, b, 240), (0, i), (ancho_panel, i))
    pantalla.blit(panel, (x_panel, y_panel))
    pygame.draw.rect(
        pantalla, 
        color_borde, 
        (x_panel, y_panel, ancho_panel, alto_panel), 
        4, 
        border_radius=sy(20)
    )
    mostrar_alternativo_adaptativo(
        pantalla, "¡FELICIDADES! 🎉",
        x_panel, y_panel + sy(20), ancho_panel, sy(60),
        fuente_titulo, (100, 160, 220), centrado=True
    )
    mostrar_texto_adaptativo(
        pantalla, "¡Has completado el memorama!",
        x_panel, y_panel + sy(80), ancho_panel, sy(40),
        fuente, (30, 30, 30), centrado=True
    )
    boton = Boton(
        "¡Reiniciar! 🔄",
        x_panel + (ancho_panel - sx(300)) // 2,
        y_panel + sy(130),
        sx(300), sy(50),
        color_normal=(100, 160, 220),
        color_hover=(30, 60, 120),
        fuente=pygame.font.SysFont("Segoe UI Emoji", int(sy(28))),
        texto_adaptativo=True
    )
    boton.draw(pantalla)
    carta_rects.append((boton.rect, {'id': 'siguiente'}))
    dibujar_caja_texto(
        pantalla, x_panel, y_panel, ancho_panel, alto_panel,
        color=(220, 240, 255, 220),
        radius=sy(16),
        texto="¡Victoria! 🎉",
        fuente=fuente_titulo,
        color_texto=(30, 30, 60)
    )

def mostrar_operacion(pantalla, ANCHO, navbar_height, sx, sy, operacion_actual, sf, rect=None):
    """Muestra la operación matemática actual."""
    if not operacion_actual:
        return
    if rect is None:
        rect = (ANCHO - sx(200), navbar_height + sy(50), sx(180), sy(40))
    dibujar_caja_texto(
        pantalla,
        rect[0], rect[1], rect[2], rect[3],
        color=(240, 240, 255, 220),
        radius=sy(10),
        texto=operacion_actual,
        fuente=obtener_fuente(sf(20), negrita=True),
        color_texto=(50, 50, 120)
    )

def mostrar_racha(pantalla, ANCHO, ALTO, sx, sy, racha_correctas, mejor_racha, rect=None):
    """Muestra la racha actual y la mejor racha en pantalla."""
    if rect is None:
        rect = (ANCHO - sx(200), ALTO - sy(70), sx(180), sy(50))
    dibujar_caja_texto(
        pantalla,
        rect[0], rect[1], rect[2], rect[3],
        color=(255, 240, 200, 220),
        radius=sy(10),
        texto=f"🔥 Racha: {racha_correctas} (Mejor: {mejor_racha})",
        fuente=obtener_fuente(sy(18)),
        color_texto=(100, 50, 0)
    )

def dibujar_debug_info(self):
        """Muestra información de depuración en pantalla."""
        debug_info = [
            f"FPS: {self.fps_actual}",
            f"Resolución: {self.ANCHO}x{self.ALTO}",
            f"Escala: {self.scaler._scale_x:.2f}x, {self.scaler._scale_y:.2f}y",
            f"Tiempo: {self.tiempo_juego:.1f}s",
            f"Estado: {self.estado}",
            f"Partículas: {len(self.particulas)}",
            f"Estrellas: {len(self.estrellas)}",
            f"Burbujas: {len(self.fondo_animado.burbujas)}"
        ]
        
        # Fondo semitransparente
        debug_panel = pygame.Surface((self.sx(200), self.sy(20) * len(debug_info)), pygame.SRCALPHA)
        debug_panel.fill((0, 0, 0, 150))
        self.pantalla.blit(debug_panel, (0, 0))
        
        # Mostrar información
        for i, info in enumerate(debug_info):
            mostrar_texto_adaptativo(
                self.pantalla,
                info,
                self.sx(5), self.sy(5) + i * self.sy(20),
                self.sx(190), self.sy(20),
                fuente_base=self.fuente_pequeña,
                color=(255, 255, 255),
                centrado=False
            )
