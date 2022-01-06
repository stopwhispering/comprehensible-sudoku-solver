from typing import List, Tuple

from sudoku_solver.board.board import Board
from sudoku_solver.board.cell import Cell
from sudoku_solver.shared.preview import Preview, IndicatorLevel
from sudoku_solver.solver.decorators import evaluate_algorithm


class NFish(Preview):
    def __init__(self, candidate: int,
                 cells_in_base_rows_or_columns: List[Cell],
                 other_cells_in_cover_columns_or_rows: List[Cell]):
        self.candidate = candidate
        self.cells_in_base_rows_or_columns = cells_in_base_rows_or_columns
        self.other_cells_in_cover_columns_or_rows = other_cells_in_cover_columns_or_rows

    def get_indicator_candidates(self) -> Tuple[Tuple[int, int, int, IndicatorLevel]]:
        """return the board positions of base row candidates"""
        pos = tuple((c.x, c.y, self.candidate, IndicatorLevel.DEFAULT) for c in self.cells_in_base_rows_or_columns)
        return pos

    def get_invalidated_candidates(self) -> Tuple[Tuple[int, int, int]]:
        """return the board positions where the candidate is invalidated"""
        positions = tuple((c.x, c.y, self.candidate) for c in self.other_cells_in_cover_columns_or_rows)
        return positions

    def execute(self):
        for cell in self.other_cells_in_cover_columns_or_rows:
            cell.flag_candidates_invalid([self.candidate])


def _invalidate_with_n_fish_in_rows(board: Board, value: int, n: int) -> NFish:
    """
    If n (e.g. 3 for a swordfish) rows exist in which the candidate under consideration occurs only in exactly the
    same n different columns (either in all those columns or in two of them), then we have found a fish. We may then
    invalidate the candidate in all other cells of those columns.
    """
    # identify rows with exactly n cells having the candidate under consideration
    rows = board.rows.values()
    leading_rows = [row for row in rows if len(row.get_cells_having_candidate(value)) == n]

    # for such a row, we check whether there are exactly two other rows that have the candidate under consideration
    # only in the same three columns (in at least two of them)
    for leading_row in leading_rows:
        cells_in_leading_row = leading_row.get_cells_having_candidate(value)
        cover_columns = [c.column for c in cells_in_leading_row]

        base_rows = [leading_row]
        maybe_base_rows = [row for row in rows if 2 <= len(row.get_cells_having_candidate(value)) <= n
                           and row is not leading_row]
        for maybe_base_row in maybe_base_rows:
            # compare columns (candidate outside the three cover columns)
            cells_with_candidate = maybe_base_row.get_cells_having_candidate(value)
            if not [c for c in cells_with_candidate if c.column not in cover_columns]:
                base_rows.append(maybe_base_row)

        # assert len(base_rows) <= n
        if len(base_rows) == n:
            # now we can invalidate the candidate under consideration in all <<other>> cells of the three
            # cover columns
            for cover_column in cover_columns:
                other_cells = [c for c in cover_column.get_cells_having_candidate(value) if c.row not in base_rows]

                if other_cells:
                    cells_in_base_rows = [c for row in base_rows for c in row.get_cells_having_candidate(value)]
                    n_fish = NFish(candidate=value,
                                   cells_in_base_rows_or_columns=cells_in_base_rows,
                                   other_cells_in_cover_columns_or_rows=other_cells)
                    # cancel here to avoid inconsistencies due to not updated cells
                    return n_fish


def _invalidate_with_n_fish_in_columns(board: Board, value: int, n: int) -> NFish:
    """
    same as for rows but with rows and column switched
    # todo remove redundancy
    """
    cols = board.columns.values()
    leading_cols = [col for col in cols if len(col.get_cells_having_candidate(value)) == n]

    for leading_col in leading_cols:
        cells_in_leading_col = leading_col.get_cells_having_candidate(value)
        cover_rows = [c.row for c in cells_in_leading_col]

        base_cols = [leading_col]
        maybe_base_cols = [col for col in cols if 2 <= len(col.get_cells_having_candidate(value)) <= n
                           and col is not leading_col]
        for maybe_base_col in maybe_base_cols:
            cells_with_candidate = maybe_base_col.get_cells_having_candidate(value)
            if not [c for c in cells_with_candidate if c.row not in cover_rows]:
                base_cols.append(maybe_base_col)

        assert len(base_cols) <= n
        if len(base_cols) == n:
            for cover_row in cover_rows:
                other_cells = [c for c in cover_row.get_cells_having_candidate(value) if c.column not in
                               base_cols]
                if other_cells:
                    cells_in_base_cols = [c for col in base_cols for c in col.get_cells_having_candidate(value)]
                    n_fish = NFish(candidate=value,
                                   cells_in_base_rows_or_columns=cells_in_base_cols,
                                   other_cells_in_cover_columns_or_rows=other_cells)
                    # cancel here to avoid inconsistencies due to not updated cells
                    return n_fish


@evaluate_algorithm
def find_n_fish(board: Board, n: int):
    """
    If n (e.g. 3) rows exist in which the candidate under consideration occurs only in exactly the same n different
    columns (either in all those columns or in two of them), then we have found a fish (3 -> swordfish). We may then
    invalidate the candidate in all other cells of those columns. (cf. x-wing)

    n = 3 --> swordfish
    n = 4 --> jellyfish
    n = 5 --> squirmbag
    n = 6 --> whale
    n = 7 --> leviathan
    """
    for value in range(1, 10):
        n_fish = _invalidate_with_n_fish_in_rows(board=board, value=value, n=n)
        if not n_fish:
            _invalidate_with_n_fish_in_columns(board=board, value=value, n=n)
        if n_fish:
            board.notify_preview(preview=n_fish)
            return
