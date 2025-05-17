import pygame
from core.scale.responsive_scaler_animated import ResponsiveScalerAnimado

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("ResponsiveScalerAnimado Test")

    scaler = ResponsiveScalerAnimado(initial_width=800, initial_height=600, uniform=True)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                scaler.update(event.w, event.h)

        scaler.tick()
        screen.fill((30, 30, 30))

        # Draw a centered rectangle that scales with window size
        rect = scaler.get_centered_rect(300, 200)
        pygame.draw.rect(screen, (0, 200, 255), rect, border_radius=15)

        # Draw some scaled text
        font_size = scaler.sf(36)
        font = pygame.font.SysFont("Arial", font_size)
        text = font.render("Responsive UI", True, (255, 255, 255))
        text_rect = text.get_rect(center=(scaler.current_width // 2, scaler.sy(50)))
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
