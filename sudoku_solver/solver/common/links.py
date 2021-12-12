from typing import Tuple

from sudoku_solver.board.cell import Cell


class Link:
    cells: Tuple[Cell, Cell]
    candidate: int

    def __init__(self, cells: Tuple[Cell, Cell], candidate: int):
        assert len(cells) == 2 and cells[0].has_candidate(candidate) and cells[1].has_candidate(candidate)
        self.cells = cells
        self.candidate = candidate


class StrongLink(Link):
    def __init__(self, cells: Tuple[Cell, Cell], candidate: int):
        super().__init__(cells=cells, candidate=candidate)

    def __repr__(self):
        cell_a = f'r{self.cells[0].y}c{self.cells[0].x}'
        return f'{cell_a}({self.candidate})r{self.cells[1].y}c{self.cells[1].x}'


class WeakLink(Link):
    def __init__(self, cells: Tuple[Cell, Cell], candidate: int):
        super().__init__(cells=cells, candidate=candidate)

    def __repr__(self):
        cell_a = f'r{self.cells[0].y}c{self.cells[0].x}'
        return f'{cell_a}({self.candidate})↔r{self.cells[1].y}c{self.cells[1].x}({self.candidate})'


def cells_form_strong_link(cell_a: Cell, cell_b: Cell, candidate: int) -> bool:
    if cell_a.row is cell_b.row and cell_a.row.get_count_of_cells_having_candidate(candidate=candidate) == 2:
        return True
    if cell_a.column is cell_b.column and cell_a.column.get_count_of_cells_having_candidate(candidate=candidate) == 2:
        return True
    if cell_a.block is cell_b.block and cell_a.block.get_count_of_cells_having_candidate(candidate=candidate) == 2:
        return True
    return False


def create_link(candidate, cell_in: Cell, cell_out: Cell) -> Link:
    """link factory"""
    if cells_form_strong_link(cell_a=cell_in, cell_b=cell_out, candidate=candidate):
        link = StrongLink(cells=(cell_in, cell_out), candidate=candidate)
    else:
        link = WeakLink(cells=(cell_in, cell_out), candidate=candidate)
    return link