import pygame
import math

from pieces import *
from board import GameState, Board
from utils import highlight_coordinates, KingLocation, detect_if_in_check

GAMESIZE = 480
PIECE_OFFSET = GAMESIZE/8


def pos_to_index(pos):
    return (math.floor(pos[0] / PIECE_OFFSET), math.floor(pos[1] / PIECE_OFFSET))


def main():

    screen = pygame.display.set_mode((GAMESIZE, GAMESIZE))
    pygame.display.set_caption("Chess")

    board = Board(GAMESIZE, PIECE_OFFSET)
    gamestate = GameState()

    board.draw_gamestate(gamestate, screen)

    first_click = True
    pos_from, pos_to = False, False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if first_click:
                    pos_from = pos_to_index(pygame.mouse.get_pos())
                    print(pos_from)
                    piece = gamestate.get_piece_type(pos_from)
                    if piece is None:
                        pos_from = False
                        continue

                    valid_moves = piece.get_valid_moves(pos_from, gamestate)

                    if valid_moves.size > 0:
                        highlight_coordinates(screen, valid_moves)

                    first_click = False
                else:
                    pos_to = pos_to_index(pygame.mouse.get_pos())
                    first_click = True

        if pos_from and pos_to and pos_from != pos_to:

            pos_to = np.array(pos_to)
            if any(np.array_equal(np.array(pos_to), move) for move in valid_moves):
                gamestate.move(pos_from, pos_to)
                detect_if_in_check(gamestate, 'b')
            else:
                print('Invalid Move!')

            board.draw_gamestate(gamestate, screen)
            pos_from, pos_to = False, False


if __name__ == '__main__':
    main()
