from typing import Tuple

from sudoku_solver.ui.ui_constants import MARGIN, CELL_LENGTH, CANDIDATE_LENGTH


def invert_y(y: int) -> int:
    """tkinter starts y at top, our board starts y at bottom
    note: both ui and board are 0-based"""
    return 8 - y


def get_candidate_rectangle_coords(x: int, y: int, n: int) -> Tuple[float, float, float, float]:
    """get rectangle pixels for candidate n'th sub-rectangle ( 012
                                                               345
                                                               678 ) """
    # offsets from requested sub-rectangle
    offset_x = n % 3
    offset_y = n // 3

    x0 = MARGIN + x * CELL_LENGTH + offset_x * CANDIDATE_LENGTH + 1
    x1 = x0 + CANDIDATE_LENGTH - 1
    y0 = MARGIN + invert_y(y) * CELL_LENGTH + offset_y * CANDIDATE_LENGTH + 1
    y1 = y0 + CANDIDATE_LENGTH - 1
    return x0, y0, x1, y1


def board_position_to_coords(x: int, y: int) -> Tuple[float, float]:
    """convert board-based position to ui pixel coordinates; includes y-inversion; returns center
    of value rectangle"""
    y_inv = invert_y(y)
    coordinates = (MARGIN + x * CELL_LENGTH + CELL_LENGTH / 2,
                   MARGIN + y_inv * CELL_LENGTH + CELL_LENGTH / 2)
    return coordinates
