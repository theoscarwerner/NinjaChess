import pygame
import random
import math
import numpy as np
from pieces import *
from utils import opposite_color


class Board():
    def __init__(self, size, offset):
        self.size = size  # size of board
        self.offset = offset  # offset when drawing pieces

        self.board = pygame.image.load('graph/board.png').convert_alpha()
        self.board = pygame.transform.scale(self.board, (self.size, self.size))
        self.board.set_alpha(128)

    def draw_gamestate(self, gamestate, screen):

        screen.fill('WHITE')
        screen.blit(self.board, (0, 0))  # The chess checkerboard background

        for row_idx, row in enumerate(gamestate.position):
            for rank_idx, piece in enumerate(row):
                if piece is not None:
                    screen.blit(piece.image, (rank_idx * self.offset, row_idx * self.offset))

        pygame.display.update()


class GameState():
    def __init__(self):
        # self.position = [
        #     [Rook('b'), Knight('b'), Bishop('b'), Queen('b'), King('b'), Bishop('b'), Knight('b'), Rook('b')],
        #     [Pawn('b'), Pawn('b'), Pawn('b'), Pawn('b'), Pawn('b'), Pawn('b'), Pawn('b'), Pawn('b')],
        #     [None, None, None, None, None, None, None, None],
        #     [None, None, None, None, None, None, None, None],
        #     [None, None, None, None, None, Queen('b'), None, None],
        #     [None, None, None, None, None, None, None, None],
        #     [Pawn('w'), Pawn('w'), Pawn('w'), None, Pawn('w'), Pawn('w'), Pawn('w'), Pawn('w')],
        #     [Rook('w'), Knight('w'), Bishop('w'), Queen('w'), King('w'), Bishop('w'), Knight('w'), Rook('w')],
        # ]
        self.position = [
            [Rook('b'), Knight('b'), Bishop('b'), Queen('b'), King('b'), Bishop('b'), Knight('b'), Rook('b')],
            [Pawn('b'), Pawn('b'), Pawn('b'), Pawn('b'), Pawn('b'), Pawn('b'), Pawn('b'), Pawn('b')],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [Pawn('w'), Pawn('w'), Pawn('w'), Pawn('w'), Pawn('w'), Pawn('w'), Pawn('w'), Pawn('w')],
            [Rook('w'), Knight('w'), Bishop('w'), Queen('w'), King('w'), Bishop('w'), Knight('w'), Rook('w')],
        ]

        self.color_mask = []
        for row in self.position:
            row_ = []
            for piece in row:
                if not piece:
                    row_.append(0)
                elif piece.color == 'w':
                    row_.append(1)
                elif piece.color == 'b':
                    row_.append(-1)
            self.color_mask.append(row_)

        self.color_mask = np.array(self.color_mask)

        self.current_turn_color = 'w'

        self.w_king_location = np.array([4, 7])
        self.b_king_location = np.array([4, 0])

    def get_king_location(self, color):
        if color == 'w':
            return self.w_king_location
        elif color == 'b':
            return self.b_king_location

    def change_to_next_players_turn(self):
        self.current_turn_color = opposite_color(self.current_turn_color)

    def get_piece_type(self, pos):
        x, y = pos
        return self.position[y][x]

    def update_position(self, piece, pos_from, pos_to):
        # Update position
        self.position[pos_from[1]][pos_from[0]] = None
        self.position[pos_to[1]][pos_to[0]] = piece

        # Update color_mask
        piece = self.color_mask[pos_from[1]][pos_from[0]]
        self.color_mask[pos_from[1]][pos_from[0]] = 0
        self.color_mask[pos_to[1]][pos_to[0]] = piece

    def create_backup_position(self):
        self.backup_position = []
        for row in self.position:
            new_row = []
            for piece in row:
                if piece is not None:
                    new_row.append(piece.copy())
                else:
                    new_row.append(None)

    def revert_position(self):
        self.position = self.backup_position

    def move(self, pos_from, pos_to):
        self.create_backup_position()

        piece = self.position[pos_from[1]][pos_from[0]]

        if isinstance(piece, Pawn):
            piece.has_moved = True

        if isinstance(piece, King):
            if piece.color == 'w':
                self.w_king_location = np.array([pos_to[0], pos_to[1]])
            elif piece.color == 'b':
                self.b_king_location = np.array([pos_to[0], pos_to[1]])

        self.update_position(piece, pos_from, pos_to)
