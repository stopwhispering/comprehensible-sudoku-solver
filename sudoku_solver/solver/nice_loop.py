from dataclasses import dataclass
from typing import Tuple

from sudoku_solver.board.board import Board
from sudoku_solver.board.cell import Cell


class StrongLink:
    def __init__(self, cells: Tuple[Cell, Cell], candidate: int):
        self.cells = cells
        self.candidate = candidate

    def __repr__(self):
        a = 1



def find_discontinuous_nice_loop(board: Board):
    # todo
    cells = board.get_cells_by_candidate(7)
    link = StrongLink(cells=cells[:2], candidate=2)