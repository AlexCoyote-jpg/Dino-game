import pygame
from core.scale.responsive_scaler_animated import ResponsiveScalerAnimado

def main():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
    pygame.display.set_caption("ResponsiveScalerAnimado Test")

    scaler = ResponsiveScalerAnimado(initial_width=1920, initial_height=1080, uniform=True)

    clock = pygame.time.Clock()
    running = True
    resized = False  # flag to toggle resolution once

    # Define button rectangle (position will be scaled)
    button_rect_base = pygame.Rect(50, 50, 300, 100)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                scaler.update(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                scaled_button_rect = scaler.scale_rect(*button_rect_base)
                if pygame.Rect(scaled_button_rect).collidepoint(mouse_pos):
                    # Toggle between two resolutions
                    if not resized:
                        screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
                        scaler.update(1280, 720)
                    else:
                        screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
                        scaler.update(1920, 1080)
                    resized = not resized

        scaler.tick()
        screen.fill((20, 20, 20))

        # Draw a centered rectangle that scales
        rect = scaler.get_centered_rect(400, 250)
        pygame.draw.rect(screen, (0, 150, 255), rect, border_radius=12)

        # Draw the button
        scaled_button = scaler.scale_rect(*button_rect_base)
        pygame.draw.rect(screen, (200, 50, 50), scaled_button, border_radius=8)

        font = pygame.font.SysFont("Arial", scaler.sf(36))
        button_text = font.render("Cambiar Resolución", True, (255, 255, 255))
        text_rect = button_text.get_rect(center=pygame.Rect(scaled_button).center)
        screen.blit(button_text, text_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
