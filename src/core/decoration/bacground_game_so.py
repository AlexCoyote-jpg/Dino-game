import pygame
import random
import math
from collections import deque
from ui.components.utils import get_gradient
from core.scale.responsive_scaler_animated import ResponsiveScalerAnimado

PALETA = {
    "azul_cielo": (90, 200, 250),
    "rosa_pastel": (255, 156, 189),
    "verde_lima": (186, 255, 86),
    "lavanda": (186, 156, 255),
    "turquesa": (52, 199, 186)
}

# Pre-calculate sin values for optimization
SIN_CACHE = [math.sin(i / 100.0) for i in range(628)]  # 0 to 2π * 100

def get_sin(angle):
    """Get sine value from cache for better performance"""
    index = int(angle * 100) % 628
    return SIN_CACHE[index]

def generar_nube_surface_eficiente(radio_base, color):
    # Round dimensions to integers to avoid unnecessary conversions
    ancho_nube = int(radio_base * 3.0)
    alto_nube = int(radio_base * 1.8)
    
    # Create surface only once
    surf = pygame.Surface((ancho_nube, alto_nube), pygame.SRCALPHA)
    
    # Pre-calculate ellipse parameters to avoid repeated calculations
    elipses = [
        (int(radio_base * 1.0), int(radio_base * 1.0), int(radio_base * 1.3), int(radio_base * 1.0)),
        (int(radio_base * 1.7), int(radio_base * 0.8), int(radio_base * 1.1), int(radio_base * 0.9)),
        (int(radio_base * 0.5), int(radio_base * 1.1), int(radio_base * 1.0), int(radio_base * 0.8)),
        (int(radio_base * 1.5), int(radio_base * 1.3), int(radio_base * 1.2), int(radio_base * 1.0)),
        (int(radio_base * 2.0), int(radio_base * 1.1), int(radio_base * 1.0), int(radio_base * 0.8)),
        (int(radio_base * 1.2), int(radio_base * 1.5), int(radio_base * 1.0), int(radio_base * 0.7)),
    ]
    
    # Draw all ellipses at once
    for cx, cy, sx, sy in elipses:
        pygame.draw.ellipse(
            surf,
            color,
            pygame.Rect(cx - sx // 2, cy - sy // 2, sx, sy)
        )
    
    # Add highlight
    pygame.draw.ellipse(
        surf, (255, 255, 255, 60),
        pygame.Rect(
            int(radio_base * 0.9), 
            int(radio_base * 0.5), 
            int(radio_base * 1.0), 
            int(radio_base * 0.4)
        )
    )
    
    # Convert once and cache
    return surf.convert_alpha(), (int(radio_base * 0.7), int(radio_base * 0.7))

class FondoAnimado:
    def __init__(self, pantalla, navbar_height=0):
        self.pantalla = pantalla
        self.navbar_height = navbar_height

        # Dimensions and internal animated scaler
        self.ANCHO = pantalla.get_width()
        self.ALTO = pantalla.get_height()
        self.scaler = ResponsiveScalerAnimado(initial_width=self.ANCHO, initial_height=self.ALTO)
        self.sx = self.scaler.sx
        self.sy = self.scaler.sy

        # Background state
        self.burbujas = deque(maxlen=20)  # Limit max bubbles for performance
        self.nubes = []
        self._generar_nubes(6)
        
        # Cache and optimization
        self.fondo_actual = None
        self.fondo_cache = None
        self.tiempo_burbuja = 0
        self.dirty_rects = []  # For optimized rendering
        self.last_bubble_positions = []  # Track previous positions for dirty rect updates
        self.last_cloud_positions = []  # Track previous positions for dirty rect updates
        
        # Time-based animation
        self.accumulated_time = 0
        self.bubble_spawn_timer = 0

    def set_escaladores(self, sx, sy):
        """Allows injecting another scaling system (optional)."""
        self.sx = sx
        self.sy = sy

    def resize(self, ancho, alto):
        """Call on VIDEORESIZE: updates size, scaler and clouds."""
        self.ANCHO, self.ALTO = ancho, alto
        self.scaler.update(ancho, alto)
        self.fondo_cache = None
        self._generar_nubes(6)
        self.dirty_rects = []  # Reset dirty rects on resize
        self.last_bubble_positions = []
        self.last_cloud_positions = []

    def _generar_nubes(self, cantidad):
        # Clear existing clouds
        self.nubes = []
        self.last_cloud_positions = []
        
        # Create cloud pool with pre-rendered surfaces
        cloud_pool = []
        for _ in range(3):  # Create 3 different cloud types to reuse
            radio = self.sx(60) * random.uniform(1.0, 1.7)
            surf, offset = generar_nube_surface_eficiente(
                radio, (255, 255, 255, random.randint(90, 140))
            )
            cloud_pool.append((surf, offset))
        
        # Create cloud instances using the pool
        for _ in range(cantidad):
            surf, offset = random.choice(cloud_pool)
            self.nubes.append({
                'x': random.randint(0, self.ANCHO),
                'y': random.randint(self.navbar_height, self.ALTO//3),
                'velocidad': random.uniform(0.15, 0.45),
                'surf': surf,
                'offset': offset,
                'w': surf.get_width(),
                'h': surf.get_height(),
                'rect': pygame.Rect(0, 0, surf.get_width(), surf.get_height())
            })
            self.last_cloud_positions.append((0, 0, 0, 0))  # Initialize tracking rects

    def update(self, dt=1.0):
        """Call each frame before draw(). Now uses delta time."""
        self.scaler.tick()
        
        # Use delta time for time-based animation
        self.accumulated_time += dt
        
        # Only update when necessary (every ~16ms for 60fps equivalent)
        if self.accumulated_time >= 1.0:
            self._actualizar_nubes(self.accumulated_time)
            self._actualizar_burbujas(self.accumulated_time)
            self.accumulated_time = 0

    def draw(self, fondo=None):
        # Only redraw background if it changed
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
            pygame.display.update()  # Full update when background changes
            self.dirty_rects = []  # Reset dirty rects
        else:
            # Redraw only the areas that changed in the last frame
            for rect in self.dirty_rects:
                self.pantalla.blit(self.fondo_cache, rect, rect)
        
        # Clear dirty rects for this frame
        self.dirty_rects = []
        
        # Draw clouds and bubbles, collecting new dirty rects
        self._dibujar_nubes()
        self._dibujar_burbujas()
        
        # Only update the changed areas
        if self.dirty_rects:
            pygame.display.update(self.dirty_rects)

    def _actualizar_nubes(self, dt):
        for i, nube in enumerate(self.nubes):
            # Store old position for dirty rect
            old_x, old_y = nube['x'], nube['y']
            
            # Update position with delta time
            nube['x'] += nube['velocidad'] * dt
            
            # Wrap around when off-screen
            if nube['x'] > self.ANCHO + self.sx(120):
                nube['x'] = -nube['w']
                nube['y'] = random.randint(self.navbar_height, self.ALTO // 3)
            
            # Update the cloud's rect for collision detection and dirty rect tracking
            nube['rect'].x = int(nube['x'] - nube['offset'][0])
            nube['rect'].y = int(nube['y'] - nube['offset'][1])
            
            # Add both old and new positions to dirty rects
            old_rect = pygame.Rect(
                int(old_x - nube['offset'][0]),
                int(old_y - nube['offset'][1]),
                nube['w'],
                nube['h']
            )
            self.dirty_rects.append(old_rect)
            self.dirty_rects.append(nube['rect'].copy())
            
            # Update tracking rect
            self.last_cloud_positions[i] = (
                nube['rect'].x, nube['rect'].y, nube['rect'].width, nube['rect'].height
            )

    def _dibujar_nubes(self):
        for nube in self.nubes:
            self.pantalla.blit(
                nube['surf'], 
                (nube['rect'].x, nube['rect'].y)
            )

    def _crear_burbuja(self):
        # Only create if we haven't reached the maximum
        if len(self.burbujas) < self.burbujas.maxlen:
            x = random.randint(self.sx(50), self.ANCHO - self.sx(50))
            y = self.ALTO + self.sy(20)
            radio = random.randint(self.sy(14), self.sy(32))
            color = random.choice(list(PALETA.values()))
            
            # Create bubble with pre-calculated values
            self.burbujas.append({
                'x': x,
                'y': y,
                'radio': radio,
                'velocidad': random.uniform(0.4, 1.3),
                'color': (*color[:3], 90),
                'oscilacion': random.uniform(0.7, 1.7),
                'fase': random.uniform(0, 6.28),  # 2π
                'rect': pygame.Rect(x - radio, y - radio, radio * 2, radio * 2)
            })
            
            # Initialize tracking for this bubble
            self.last_bubble_positions.append((x - radio, y - radio, radio * 2, radio * 2))

    def _actualizar_burbujas(self, dt):
        # Update bubble spawn timer
        self.bubble_spawn_timer -= dt
        if self.bubble_spawn_timer <= 0:
            self._crear_burbuja()
            self.bubble_spawn_timer = random.uniform(0.6, 1.8)  # Time-based spawn
        
        # Get current time once
        ticks = pygame.time.get_ticks() / 520
        
        # Track which bubbles to keep
        new_burbujas = deque(maxlen=self.burbujas.maxlen)
        new_positions = []
        
        # Update bubble positions
        for i, b in enumerate(self.burbujas):
            # Store old position for dirty rect
            old_x, old_y = b['x'], b['y']
            old_rect = pygame.Rect(
                int(old_x - b['radio']), 
                int(old_y - b['radio']), 
                b['radio'] * 2, 
                b['radio'] * 2
            )
            
            # Update position with delta time
            new_y = b['y'] - b['velocidad'] * dt
            new_x = b['x'] + get_sin(ticks + b['fase']) * b['oscilacion']
            
            # Only keep bubbles that are still on screen
            if new_y > -b['radio']:
                b['y'] = new_y
                b['x'] = new_x
                
                # Update rect
                b['rect'].x = int(new_x - b['radio'])
                b['rect'].y = int(new_y - b['radio'])
                
                new_burbujas.append(b)
                new_positions.append((b['rect'].x, b['rect'].y, b['rect'].width, b['rect'].height))
                
                # Add both old and new positions to dirty rects
                self.dirty_rects.append(old_rect)
                self.dirty_rects.append(b['rect'].copy())
            else:
                # Add old position to dirty rects for cleanup
                self.dirty_rects.append(old_rect)
        
        # Update bubble collections
        self.burbujas = new_burbujas
        self.last_bubble_positions = new_positions

    def _dibujar_burbujas(self):
        for b in self.burbujas:
            # Draw main bubble
            x, y, radio = int(b['x']), int(b['y']), b['radio']
            pygame.draw.circle(self.pantalla, b['color'], (x, y), radio)
            
            # Draw highlight
            highlight_x = int(x - radio // 4)
            highlight_y = int(y - radio // 4)
            highlight_radio = radio // 3
            pygame.draw.circle(
                self.pantalla, (255, 255, 255, 120),
                (highlight_x, highlight_y),
                highlight_radio
            )