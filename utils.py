import pygame

RED = (255, 0, 0)


def highlight_coordinates(screen, coordinates):
    for x, y in coordinates:
        rect = (x * 60, y * 60, 60, 60)
        shape_surf = pygame.Surface(pygame.Rect(rect).size)
        shape_surf.set_alpha(128)
        pygame.draw.rect(shape_surf, RED, shape_surf.get_rect())
        screen.blit(shape_surf, rect)

    pygame.display.update()
    return shape_surf
