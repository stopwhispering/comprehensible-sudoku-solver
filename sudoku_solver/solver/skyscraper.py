import itertools
from typing import Set, Tuple

from sudoku_solver.board.board import Board
from sudoku_solver.board.cell import Cell
from sudoku_solver.shared.preview import Preview
from sudoku_solver.solver.decorators import evaluate_algorithm


@evaluate_algorithm
def find_skyscraper(board: Board):
    skyscraper = find_skyscraper_rows_type(board=board)
    if not skyscraper:
        skyscraper = find_skyscraper_cols_type(board=board)
    if skyscraper:
        board.notify_preview(preview=skyscraper)


class Skyscraper(Preview):
    def __init__(self, candidate: int, cells_seeing_both_roof_cells: Set[Cell]):
        self.candidate = candidate
        self.cells_seeing_both_roof_cells = cells_seeing_both_roof_cells

    def get_invalidated_candidates(self) -> Tuple[Tuple[int, int, int]]:
        """return the board positions where the candidate is invalidated"""
        positions = tuple((c.x, c.y, self.candidate) for c in self.cells_seeing_both_roof_cells)
        return positions

    def execute(self):
        for cell in self.cells_seeing_both_roof_cells:
            cell.flag_candidates_invalid([self.candidate])


def find_skyscraper_rows_type(board: Board) -> Skyscraper:
    """apply the skyscraper logic (version of turbot fish)"""
    for value in range(1, 10):

        # find rows with 2 cells having that candidate
        rows = [row for row in board.rows.values() if len(row.get_cells_having_candidate(value)) == 2]
        if len(rows) < 2:
            continue
        # for each combination of two of the rows found...
        row_combinations = tuple(itertools.combinations(rows, 2))
        for row_combination in row_combinations:
            # ...check whether one cell in each row shares the column with the other
            cells1 = [c for c in row_combination[0].get_cells_having_candidate(value)]
            cells2 = [c for c in row_combination[1].get_cells_having_candidate(value)]
            cols1 = set([c.column for c in cells1])
            cols2 = ([c.column for c in cells2])
            skyscraper_base = cols1.intersection(cols2)  # must be length 1, i.e. same column
            skyscraper_roof = cols1.symmetric_difference(cols2)  # must be length 2, i.e. diff. column
            if not len(skyscraper_base) == 1 or not len(skyscraper_roof) == 2:
                continue

            # ...if the cells with the different columns (i.e. the roof) are in the same band (i.e. either block
            # 0,1,2 or 3,4,5 or 6,7,8, then we have a skyscraper
            cells_roof = [c for c in cells1 + cells2 if c.column in skyscraper_roof]
            assert len(cells_roof) == 2
            # if board.get_cells_same_band(cells=cells_roof, mode='vertical'):

            # we may now invalidate the candidate under consideration for all cells that "see" both roof cells
            cells_seeing_roof_cell1_raw = (cells_roof[0].column.get_cells_having_candidate(value) + cells_roof[
                0].block.get_cells_having_candidate(value))
            cells_seeing_roof_cell1 = set([c for c in cells_seeing_roof_cell1_raw if c not in cells1 + cells2])

            cells_seeing_roof_cell2_raw = (cells_roof[1].column.get_cells_having_candidate(value) + cells_roof[
                1].block.get_cells_having_candidate(value))
            cells_seeing_roof_cell2 = set([c for c in cells_seeing_roof_cell2_raw if c not in cells1 + cells2])

            cells_seeing_both_roof_cells = cells_seeing_roof_cell1.intersection(cells_seeing_roof_cell2)
            if cells_seeing_both_roof_cells:
                skyscraper = Skyscraper(candidate=value,
                                        cells_seeing_both_roof_cells=cells_seeing_both_roof_cells)
                # cancel here to avoid inconsistencies due to not updated cells
                return skyscraper


def find_skyscraper_cols_type(board: Board) -> Skyscraper:
    """same as rows_type but with cols/rows switched"""
    for value in range(1, 10):

        # find cols with 2 cells having that candidate
        cols = [col for col in board.columns.values() if len(col.get_cells_having_candidate(value)) == 2]
        if len(cols) < 2:
            continue
        # for each combination of two of the cols found...
        col_combinations = tuple(itertools.combinations(cols, 2))
        for col_combination in col_combinations:
            # ...check whether one cell in each col shares the row with the other
            cells1 = [c for c in col_combination[0].get_cells_having_candidate(value)]
            cells2 = [c for c in col_combination[1].get_cells_having_candidate(value)]
            rows1 = set([c.row for c in cells1])
            rows2 = ([c.row for c in cells2])
            skyscraper_base = rows1.intersection(rows2)  # must be length 1, i.e. same row
            skyscraper_roof = rows1.symmetric_difference(rows2)  # must be length 2, i.e. diff. row
            if not len(skyscraper_base) == 1 or not len(skyscraper_roof) == 2:
                continue

            # ...if the cells with the different rows (i.e. the roof) are in the same band (i.e. either block
            # 0,1,2 or 3,4,5 or 6,7,8, then we have a skyscraper
            cells_roof = [c for c in cells1 + cells2 if c.row in skyscraper_roof]
            assert len(cells_roof) == 2
            # if board.get_cells_same_band(cells=cells_roof, mode='vertical'):

            # we may now invalidate the candidate under consideration for all cells that "see" both roof cells
            cells_seeing_roof_cell1_raw = (cells_roof[0].row.get_cells_having_candidate(value) + cells_roof[
                0].block.get_cells_having_candidate(value))
            cells_seeing_roof_cell1 = set([c for c in cells_seeing_roof_cell1_raw if c not in cells1 + cells2])

            cells_seeing_roof_cell2_raw = (cells_roof[1].row.get_cells_having_candidate(value) + cells_roof[
                1].block.get_cells_having_candidate(value))
            cells_seeing_roof_cell2 = set([c for c in cells_seeing_roof_cell2_raw if c not in cells1 + cells2])

            cells_seeing_both_roof_cells = cells_seeing_roof_cell1.intersection(cells_seeing_roof_cell2)
            if cells_seeing_both_roof_cells:
                skyscraper = Skyscraper(candidate=value,
                                        cells_seeing_both_roof_cells=cells_seeing_both_roof_cells)
                # cancel here to avoid inconsistencies due to not updated cells
                return skyscraper
