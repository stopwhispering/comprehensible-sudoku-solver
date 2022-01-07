import itertools
from typing import List, Sequence

from sudoku_solver.board.board import Board
from sudoku_solver.board.cell import Cell
from sudoku_solver.shared.preview import Preview, IndicatorLevel, HighlightedPosition
from sudoku_solver.shared.puzzle import ValuePosition
from sudoku_solver.solver.decorators import evaluate_algorithm


class TwoStringKite(Preview):
    def __init__(self,
                 candidate: int,
                 shared_block_cells: List[Cell],
                 kite_cells: List[Cell], ):
        assert len(shared_block_cells) == len(kite_cells) == 2
        self.candidate = candidate
        self.shared_block_cells = shared_block_cells
        self.kite_cells = kite_cells

    def get_indicator_candidates(self) -> Sequence[HighlightedPosition]:
        """return the board positions of kite and util-block cells in different colors"""
        pos_shared = [HighlightedPosition(x=cell.x,
                                          y=cell.y,
                                          value=self.candidate,
                                          indicator_level=IndicatorLevel.DEFAULT) for cell in self.shared_block_cells]
        pos_kite = [HighlightedPosition(x=cell.x,
                                        y=cell.y,
                                        value=self.candidate,
                                        indicator_level=IndicatorLevel.ALTERNATIVE) for cell in self.kite_cells]
        return pos_shared + pos_kite

    def _get_invalidated_cells(self) -> List[Cell]:
        seen_by_a = self.kite_cells[0].seen_by(self.candidate)
        seen_by_b = self.kite_cells[1].seen_by(self.candidate)
        seen_by_both_raw = seen_by_a.intersection(seen_by_b)
        seen_by_both = [c for c in seen_by_both_raw if c not in self.kite_cells and c not in self.shared_block_cells]
        return seen_by_both

    def get_invalidated_candidates(self) -> Sequence[ValuePosition]:
        """return the board positions where the candidate is invalidated"""
        # invalidate candidate in cells that see both kite cells
        invalidated_cells = self._get_invalidated_cells()
        pos = [ValuePosition(x=c.x, y=c.y, value=self.candidate) for c in invalidated_cells]
        return pos

    def execute(self):
        invalidated_cells = self._get_invalidated_cells()
        for cell in invalidated_cells:
            cell.flag_candidates_invalid([self.candidate])


@evaluate_algorithm
def find_two_string_kite(board: Board):
    """we need a row and a colum, both having a specific candidate exactly two times. additionally,
    one candidate each must be in the same block."""

    for candidate in range(1, 10):

        row_cells_list = [row.get_cells_having_candidate(candidate) for row in board.rows.values()
                          if len(row.get_cells_having_candidate(candidate)) == 2]
        col_cells_list = [col.get_cells_having_candidate(candidate) for col in board.columns.values()
                          if len(col.get_cells_having_candidate(candidate)) == 2]

        if not row_cells_list or not col_cells_list:
            continue

        # for each combination of row and column, check if ...
        #   a. the two cells per row and per col must lie in different blocks each
        #   b. we have 4 different cellt
        #   c. one row cell and column cell are in the same block
        row_col_combinations = itertools.product(row_cells_list, col_cells_list)
        for row_col_combination in row_col_combinations:

            blocks = [[c.block for c in element] for element in row_col_combination]
            if len(set(blocks[0])) != 2 or len(set(blocks[1])) != 2:
                continue

            if len(set([c for cells in row_col_combination for c in cells])) < 4:
                continue

            shared_block = set(blocks[0]).intersection(blocks[1])
            if len(shared_block) != 1:
                continue

            # we have a two-string kite. we may now invalidate our candidate in all cells that see both
            # cells in row and col that do not share the same block
            shared_block_cells = [c for cells in row_col_combination for c in cells if c.block in shared_block]
            kite_cells = [c for cells in row_col_combination for c in cells if c not in shared_block_cells]
            two_string_kite = TwoStringKite(candidate=candidate,
                                            shared_block_cells=shared_block_cells,
                                            kite_cells=kite_cells, )

            # continue with next combination if our two-string kite wouldn't invalidate anything
            if two_string_kite.get_invalidated_candidates():
                board.notify_preview(preview=two_string_kite)
                return
