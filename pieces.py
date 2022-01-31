import pygame
import numpy as np


class Piece:
    def __init__(self, color):
        assert color == 'w' or color == 'b'
        self.color = color
        if color == 'w':
            self.color_representation = 1
        elif color == 'b':
            self.color_representation = -1
        self.image = pygame.image.load(f'graph/{color}{self.char}.png').convert_alpha()

    def remove_same_color_from_coordinates(self, valid_moves, gamestate):
        if valid_moves.size == 0:
            return valid_moves
        valid_moves_msk = gamestate.color_mask[valid_moves[:, 1],
                                               valid_moves[:, 0]] * self.color_representation

        valid_moves = valid_moves[np.where(valid_moves_msk <= 0)]
        return valid_moves

    def get_valid_moves(self, pos_from, gamestate):
        current_coordinates = np.array(pos_from)
        valid_moves = self._get_valid_moves(current_coordinates, gamestate)
        return valid_moves

    def remove_out_of_bounds_moves(self, available_coordinates):
        invalid_moves = np.where((available_coordinates >= 8) | (available_coordinates < 0))
        valid_moves = np.delete(available_coordinates, invalid_moves[0], axis=0)
        return valid_moves


class King(Piece):
    def __init__(self, color):
        self.char = 'K'
        super().__init__(color)
        if self.color == 'w':
            self.location = np.array([7, 4])
        elif self.color == 'b':
            self.location = np.array([0, 4])

    def check_validity(self, x1, y1, x2, y2):
        return abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1

    def _get_valid_moves(self, current_coordinates, gamestate):
        x, y = current_coordinates
        available_coordinates = []
        for x_ in [-1, 0, 1]:
            for y_ in [-1, 0, 1]:
                if x == 0 and y == 0:
                    continue
                available_coordinates.append([x + x_, y + y_])

        available_coordinates = np.array(available_coordinates)
        valid_moves = self.remove_out_of_bounds_moves(available_coordinates)
        valid_moves = self.remove_same_color_from_coordinates(valid_moves, gamestate)

        return np.array(valid_moves)

    def __str__(self):
        return f'{self.color} King'


class Queen(Piece):
    def __init__(self, color):
        self.char = 'Q'
        super().__init__(color)

    def check_validity(self, x1, y1, x2, y2):
        # Bishop and rook validity with or
        return (abs(x1 - x2) == abs(y1 - y2)) or (x1 == x2 or y1 == y2)

    def _get_valid_moves(self, current_coordinates, gamestate):
        rook_moves = Rook(self.color)._get_valid_moves(current_coordinates, gamestate)
        bishop_moves = Bishop(self.color)._get_valid_moves(current_coordinates, gamestate)
        if bishop_moves.size == 0:
            return rook_moves
        elif rook_moves.size == 0:
            return bishop_moves
        return np.concatenate((rook_moves, bishop_moves))

    def __str__(self):
        return f'{self.color} Queen'


class Rook(Piece):
    def __init__(self, color):
        self.char = 'R'
        super().__init__(color)

    def check_validity(self, x1, y1, x2, y2):
        return x1 == x2 or y1 == y2

    def _get_valid_moves(self, current_coordinates, gamestate):
        x, y = current_coordinates
        available_coordinates = [
            reversed([[x, y_] for y_ in range(0, y)]),
            [[x, y_] for y_ in range(y + 1, 8)],
            reversed([[x_, y] for x_ in range(0, x)]),
            [[x_, y] for x_ in range(x + 1, 8)],
        ]
        valid_moves = []

        for direction in available_coordinates:
            for coordinate in direction:
                x, y = coordinate
                # If there is a piece on current coordinate
                piece = gamestate.position[y][x]
                if piece:
                    # if piece is same color, disallow capture
                    if piece.color == self.color:
                        break
                    # Allow capture
                    else:
                        valid_moves.append(coordinate)
                        break

                valid_moves.append(coordinate)

        return np.array(valid_moves)

    def __str__(self):
        return f'{self.color} Rook'


class Knight(Piece):
    def __init__(self, color):
        self.char = 'N'
        # When a Knight moves, the change in piece position is one of below
        self.index_changes_when_move = np.array([
            [1, 2], [-1, 2], [-1, -2], [1, -2], [2, 1], [-2, 1], [-2, -1], [2, -1]])
        super().__init__(color)

    def check_validity(self, x1, y1, x2, y2):
        return set([abs(x1 - x2), abs(y1 - y2)]) == set([1, 2])

    def _get_valid_moves(self, current_coordinates, gamestate):
        # Get indexes of places knight can move
        available_coordinates = current_coordinates + self.index_changes_when_move

        # Remove invalid moves, such as moves outside the board
        valid_moves = self.remove_out_of_bounds_moves(available_coordinates)
        valid_moves = self.remove_same_color_from_coordinates(valid_moves, gamestate)

        return valid_moves

    def __str__(self):
        return f'{self.color} Knight'


class Bishop(Piece):
    def __init__(self, color):
        self.char = 'B'
        super().__init__(color)

    def check_validity(self, x1, y1, x2, y2):
        return abs(x1 - x2) == abs(y1 - y2)

    def _get_valid_moves(self, current_coordinates, gamestate):
        # 4 directions

        path = np.array([[1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7]])
        index_changes_when_move = np.array([
            path * [-1, -1],
            path * [-1, 1],
            path * [1, -1],
            path * [1, 1],
        ])

        available_coordinates = index_changes_when_move + current_coordinates
        valid_moves = []
        for direction in available_coordinates:
            for coordinate in direction:
                # if coordinate not in board
                if not all((coordinate < 8) & (coordinate >= 0)):
                    break

                x, y = coordinate
                # If there is a piece on current coordinate
                piece = gamestate.position[y][x]
                if piece:
                    # if piece is same color, disallow capture
                    if piece.color == self.color:
                        break
                    # Allow capture
                    else:
                        valid_moves.append(coordinate)
                        break

                valid_moves.append(coordinate)

        return np.array(valid_moves)

    def __str__(self):
        return f'{self.color} Bishop'


class Pawn(Piece):
    def __init__(self, color):
        self.char = 'p'
        self.has_moved = False
        super().__init__(color)

    def check_validity(self, x1, y1, x2, y2):
        if x1 == x2:
            if not self.has_moved:
                self.has_moved = True
                if self.color == 'w':
                    if y1 - y2 in [1, 2]:
                        return True
                elif self.color == 'b':
                    if y1 - y2 in [-1, -2]:
                        return True
            else:
                if self.color == 'w':
                    if y1 - y2 == 1:
                        return True
                elif self.color == 'b':
                    if y1 - y2 == -1:
                        return True
        return False

    def _get_valid_moves(self, current_coordinates, gamestate):
        # MISSING EN PASSENT
        x, y = current_coordinates

        valid_moves = []

        if self.color == 'w':
            if y != 0:
                if gamestate.position[y - 1][x] is None:
                    valid_moves.append([x, y - 1])

                if x != 0 and gamestate.position[y - 1][x - 1] is not None:
                    valid_moves.append([x - 1, y - 1])

                if x != 7 and gamestate.position[y - 1][x + 1] is not None:
                    valid_moves.append([x + 1, y - 1])

        elif self.color == 'b':
            if y != 7:
                if gamestate.position[y + 1][x] is None:
                    valid_moves.append([x, y + 1])

                if x != 0 and gamestate.position[y + 1][x - 1] is not None:
                    valid_moves.append([x - 1, y + 1])

                if x != 7 and gamestate.position[y + 1][x + 1] is not None:
                    valid_moves.append([x + 1, y + 1])

        if not self.has_moved:
            if self.color == 'w':
                if gamestate.position[y - 2][x] is None:
                    valid_moves.append([x, y - 2])

            elif self.color == 'b':
                if gamestate.position[y + 2][x] is None:
                    valid_moves.append([x, y + 2])

        valid_moves = self.remove_same_color_from_coordinates(
            np.array(valid_moves), gamestate)

        return np.array(valid_moves)

    def __str__(self):
        return f'{self.color} Pawn'
