from sudoku_solver.board.board import Board
from sudoku_solver.solver.artefacts import NFish


def _invalidate_with_n_fish_in_rows(board: Board, value: int, n: int) -> NFish:
    """
    If n (e.g. 3) rows exist in which the candidate under consideration occurs only in exactly the same n different
    columns (either in all those columns or in two of them), then we have found a fish (3 -> swordfish). We may then
    invalidate the candidate in all other cells of those columns. (cf. x-wing)
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
            # compare columns (candidate outside of the three cover columns)
            cells_with_candidate = maybe_base_row.get_cells_having_candidate(value)
            if not [c for c in cells_with_candidate if c.column not in cover_columns]:
                base_rows.append(maybe_base_row)

        assert len(base_rows) <= n
        if len(base_rows) == n:
            # now we can invalidate the value under consideration in all <<other>> cells of the three
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


def find_n_fish(board: Board, n: int):
    """
    If n (e.g. 3) rows exist in which the candidate under consideration occurs only in exactly the same n different
    columns (either in all those columns or in two of them), then we have found a fish (3 -> swordfish). We may then
    invalidate the candidate in all other cells of those columns. (cf. x-wing)
    """
    for value in range(1, 10):
        n_fish = _invalidate_with_n_fish_in_rows(board=board, value=value, n=n)
        if not n_fish:
            _invalidate_with_n_fish_in_columns(board=board, value=value, n=n)
        if n_fish:
            board.notify_preview(preview=n_fish)
            return
