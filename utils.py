import pygame
from dataclasses import dataclass
import numpy as np
from pieces import Queen

RED = (255, 0, 0)


@dataclass
class KingLocation:
    wKing: np.array
    bKing: np.array

    def get_location(self, color):
        if color == 'w':
            return self.wKing
        elif color == 'b':
            return self.bKing


def detect_if_in_check(gamestate, color):
    king_location = gamestate.get_king_location(color)
    for y, row in enumerate(gamestate.position):
        for x, piece in enumerate(row):
            if piece and piece.color != color:
                valid_moves = piece.get_valid_moves((x, y), gamestate)
                if valid_moves.size > 0 and (valid_moves == king_location).all(1).any():
                    print('Check!!')
                    return True
    return False


def highlight_coordinates(screen, coordinates):
    for x, y in coordinates:
        rect = (x * 60, y * 60, 60, 60)
        shape_surf = pygame.Surface(pygame.Rect(rect).size)
        shape_surf.set_alpha(128)
        pygame.draw.rect(shape_surf, RED, shape_surf.get_rect())
        screen.blit(shape_surf, rect)

    pygame.display.update()
    return shape_surf
