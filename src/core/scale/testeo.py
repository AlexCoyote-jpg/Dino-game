# Ejemplo de uso para un juego específico
from core.juego_base import JuegoBase
import pygame
import random
from ui.components.utils import obtener_fuente

class JuegoEjemplo(JuegoBase):
    def __init__(self, nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu):
        super().__init__(nombre, pantalla, config, dificultad, fondo, navbar, images, sounds, return_to_menu)
        
        # Inicializar elementos específicos del juego
        self.puntuacion = 0
        self.total_preguntas = 10
        self.pregunta_actual = 1
        self.respuesta_correcta = 42
        self.opciones = self.generar_opciones(self.respuesta_correcta, 4)
        # Fuente para instrucciones (usa el scaler animado de la base)
        self.fuente_instrucciones = obtener_fuente(self.sf(16))
        
        # Elementos UI específicos de este juego
        self.init_responsive_ui()
        
    def init_responsive_ui(self):
        """Inicializa elementos UI específicos de este juego."""
        super().init_responsive_ui()  # Llamar al método de la clase base primero
        
        # Añadir elementos específicos de este juego
        self.ui_elements.update({
            "pregunta_rect": (self.sx(100), self.navbar_height + self.sy(100), 
                             self.ANCHO - self.sx(200), self.sy(100)),
            "opciones_y": self.ALTO // 2 + self.sy(50),
            "instrucciones_rect": (self.sx(50), self.ALTO - self.sy(100), 
                                  self.ANCHO - self.sx(100), self.sy(50))
        })
        
    def on_resize(self, ancho, alto):
        """Maneja el redimensionamiento específico para este juego."""
        super().on_resize(ancho, alto)
        # actualizar fuente y UI responsiva tras cambiar el tamaño
        self.fuente_instrucciones = obtener_fuente(self.sf(16))
        self.init_responsive_ui()
        
    def update(self, dt=None):
        """Actualiza scaler y lógica del juego."""
        super().update(dt)
        # ... aquí podrías añadir lógica específica de JuegoEjemplo ...
        
    def draw(self, surface=None):
        """Dibuja la interfaz del juego."""
        surface = surface or self.pantalla
        
        # Dibujar fondo
        self.dibujar_fondo()
        
        # Dibujar título
        self.mostrar_titulo()
        
        # Dibujar pregunta
        pregunta_rect = self.ui_elements["pregunta_rect"]
        self.mostrar_texto(
            f"Pregunta {self.pregunta_actual}/{self.total_preguntas}: ¿Cuál es la respuesta a la vida, el universo y todo lo demás?",
            pregunta_rect[0], pregunta_rect[1], pregunta_rect[2], pregunta_rect[3],
            self.fuente, (30, 30, 90), centrado=True
        )
        
        # Dibujar opciones
        self.dibujar_opciones(
            opciones=self.opciones,
            y0=self.ui_elements["opciones_y"]
        )
        
        # Dibujar puntaje
        self.mostrar_puntaje(self.puntuacion, self.total_preguntas)
        
        # Dibujar racha
        self.mostrar_racha()
        
        # Dibujar operación actual
        self.mostrar_operacion()
        
        # Dibujar instrucciones
        instrucciones_rect = self.ui_elements["instrucciones_rect"]
        self.mostrar_texto(
            "Haz clic en la opción correcta. Presiona ESC para volver al menú.",
            instrucciones_rect[0], instrucciones_rect[1], 
            instrucciones_rect[2], instrucciones_rect[3],
            fuente=self.fuente_instrucciones,
            color=(100, 100, 100), 
            centrado=True
        )
        
    def handle_event(self, evento):
        """Maneja eventos específicos del juego."""
        super().handle_event(evento)  # Llamar al método de la clase base primero
        
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for i, btn in enumerate(self.opcion_botones):
                if btn.collidepoint(evento.pos):
                    self.verificar_respuesta(self.opciones[i])
                    break
    
    def verificar_respuesta(self, respuesta):
        """Verifica si la respuesta seleccionada es correcta."""
        es_correcta = respuesta == self.respuesta_correcta
        
        if es_correcta:
            self.puntuacion += 1
            
        # Generar nueva pregunta
        if self.pregunta_actual < self.total_preguntas:
            self.pregunta_actual += 1
            self.respuesta_correcta = random.randint(1, 100)
            self.opciones = self.generar_opciones(self.respuesta_correcta, 4)
        else:
            # Juego terminado
            print(f"¡Juego terminado! Puntuación final: {self.puntuacion}/{self.total_preguntas}")

# Función para probar el sistema responsivo
def test_responsive_game():
    pygame.init()
    pantalla = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption("Test Responsivo")
    
    # Crear instancia del juego de ejemplo
    juego = JuegoEjemplo(
        nombre="Juego de Prueba",
        pantalla=pantalla,
        config={},
        dificultad="Normal",
        fondo=None,
        navbar=None,
        images={},
        sounds={},
        return_to_menu=lambda: print("Volviendo al menú")
    )
    
    ejecutando = True
    reloj = pygame.time.Clock()
    
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                ejecutando = False
                
            juego.handle_event(evento)
            
        juego.update()
        juego.draw()
        
        pygame.display.flip()
        reloj.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    test_responsive_game()