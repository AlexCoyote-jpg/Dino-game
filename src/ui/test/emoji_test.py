import sys
import os
import pygame
from ui.components.emoji import mostrar_alternativo_adaptativo
from ui.components.utils import dibujar_caja_texto

min_font_size = 6  # o incluso 4

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("Prueba mostrar_alternativo_adaptativo")

    texto = (
        "Ejemplo de matemáticas y emojis:\n"
        "∑ x² + ∞ = π ≈ 3.14\n"
        "Operaciones: 5 × 2 = 10, 8 ÷ 4 = 2, 7 − 3 = 4, 9 + 1 = 10\n"
        "Inecuaciones: x ≥ 0, y ≤ ∞, α ≠ β, θ ∈ ℝ\n"
        "Fracciones: ½, ¼, ¾, √2, ∛8\n"
        "Con emojis: 😊 ∑ ∞ π ❤️ 😂 🦖 x² = ∑ + ∞ 🇲🇽 👨‍💻"
    )

    cajas = [
        pygame.Rect(40, 40, 350, 150),
        pygame.Rect(420, 40, 420, 100),
        pygame.Rect(200, 220, 500, 320),
    ]

    clock = pygame.time.Clock()
    running = True
    while running:
        pantalla.fill((255, 255, 255))
        for caja in cajas:
            # Dibuja el borde de la caja
            pygame.draw.rect(pantalla, (180, 180, 180), caja, 2)
            # Muestra el texto adaptativo dentro de la caja
            mostrar_alternativo_adaptativo(
                pantalla,
                texto,
                x=caja.x + 5,
                y=caja.y + 5,
                w=caja.width - 10,
                h=caja.height - 10,
                color=(30, 30, 30),
                centrado=True
            )
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(30)
    pygame.quit()

if __name__ == "__main__":
    main()