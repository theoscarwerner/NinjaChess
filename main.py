import pygame
import math
import numpy as np
import time

from pieces import *
from board import GameState, Board
from utils import highlight_coordinates, detect_if_in_check, opposite_color

import random

GAMESIZE = 480
PIECE_OFFSET = GAMESIZE/8


x_to_rank = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
y_to_row = {0: 8, 1: 7, 2: 6, 3: 5, 4: 4, 5: 3, 6: 2, 7: 1}


def translate_move(pos_from, pos_to):
    from_move_translation = "{rank}{row}".format(
        rank=x_to_rank[pos_from[0]], row=y_to_row[pos_from[1]])

    to_move_translation = "{rank}{row}".format(
        rank=x_to_rank[pos_to[0]], row=y_to_row[pos_to[1]])

    translation = f"{from_move_translation} -> {to_move_translation}"
    print(translation)
    return translation


def pos_to_index(pos):
    return (math.floor(pos[0] / PIECE_OFFSET), math.floor(pos[1] / PIECE_OFFSET))


def evaluate(gamestate):
    eval = 0
    for row in gamestate.position:
        for piece in row:
            if piece is not None:
                if piece.color == 'w':
                    eval -= piece.value
                else:
                    eval += piece.value
    return eval


class Opponent():
    def find_move(self, gamestate):
        best_moves = []
        best_eval = 0
        for y, row in enumerate(gamestate.position):
            for x, piece in enumerate(row):
                pos_from = (x, y)
                if piece is not None and piece.color == 'b':
                    valid_moves = piece.get_valid_moves(pos_from, gamestate)
                    for pos_to in valid_moves:
                        gamestate.move(pos_from, pos_to)
                        cur_eval = evaluate(gamestate)
                        # Current move is as good as best found
                        if cur_eval == best_eval:
                            best_moves.append((pos_from, pos_to))

                        elif cur_eval > best_eval:
                            best_eval = cur_eval
                            best_moves = [(pos_from, pos_to)]

                        gamestate.move(pos_to, pos_from)

        return random.choice(best_moves)


class Main():
    def __init__(self):
        self.screen = pygame.display.set_mode((GAMESIZE, GAMESIZE))
        pygame.display.set_caption("Chess")

        self.board = Board(GAMESIZE, PIECE_OFFSET)
        self.gamestate = GameState()

        self.board.draw_gamestate(self.gamestate, self.screen)

        self.opponent = Opponent()

    def run(self):
        first_click = True
        pos_from, pos_to = False, False
        is_in_check = False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if first_click:
                        pos_from = pos_to_index(pygame.mouse.get_pos())
                        piece = self.gamestate.get_piece_type(pos_from)

                        if piece is None:
                            pos_from = False
                            continue

                        if piece.color != self.gamestate.current_turn_color:
                            print('Not your Turn')
                            pos_from = False
                            continue

                        valid_moves = piece.get_valid_moves(pos_from, self.gamestate)

                        if valid_moves.size > 0:
                            highlight_coordinates(self.screen, valid_moves)

                        first_click = False

                    # Second click
                    else:
                        pos_to = pos_to_index(pygame.mouse.get_pos())
                        first_click = True

            if pos_from and pos_to and pos_from != pos_to:
                pos_to = np.array(pos_to)
                if any(np.array_equal(np.array(pos_to), move) for move in valid_moves):
                    self.gamestate.move(pos_from, pos_to)

                    is_illegal_king_move = False
                    if isinstance(piece, King):
                        is_illegal_king_move = detect_if_in_check(
                            self.gamestate, self.gamestate.current_turn_color)

                    is_still_in_check = False
                    if is_in_check:

                        # Missing checkmate logic (i.e detect if checkmate)
                        is_still_in_check = detect_if_in_check(
                            self.gamestate, self.gamestate.current_turn_color)

                    if is_illegal_king_move or is_still_in_check:
                        # if piece is still in check, revert back.
                        if is_still_in_check:
                            print("Invalid Move! Still in check!")
                        elif is_illegal_king_move:
                            print("That square is covered by oppenent!")

                        # Undo move
                        self.gamestate.move(pos_to, pos_from)
                        self.board.draw_gamestate(self.gamestate, self.screen)
                        pos_from, pos_to = False, False
                        continue

                    is_in_check = False

                    # other_color = opposite_color(self.gamestate.current_turn_color)
                    self.board.draw_gamestate(self.gamestate, self.screen)

                    opponent_from, opponent_to = self.opponent.find_move(self.gamestate)
                    self.gamestate.move(opponent_from, opponent_to)
                    translate_move(opponent_from, opponent_to)
                    is_in_check = detect_if_in_check(self.gamestate, 'w')

                else:
                    print('Invalid Move!')

                self.board.draw_gamestate(self.gamestate, self.screen)
                pos_from, pos_to = False, False


if __name__ == '__main__':
    main = Main()
    main.run()
