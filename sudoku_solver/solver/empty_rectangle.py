from sudoku_solver.board.board import Board
from sudoku_solver.board.houses import HouseType
from sudoku_solver.board.preview import CommonPreview, IndicatorLevel


def find_empty_rectangle(board: Board):
    """
    if one candidate is restricted to one row and one column within a block, the remaining cells within form an ER.
    we can then check for invalidations:
        find a conjugate pair (a row or column containing only two candidates, one of them being our candidate) where
        one of the candidates is in the row/col forming the ER.
        If the col/row of the ER contains a candidate, that can see the second candidate of the conjugate pair,
        it can be invalidated.
    """

    # find empty rectangles on the board
    for block in board.get_all_houses(house_type=HouseType.BLOCK):
        for candidate in block.candidates:
            cells = block.get_cells_having_candidate(candidate=candidate)
            if len(cells) < 3:
                continue
            rows = [c.row for c in cells]
            cols = [c.column for c in cells]
            if len(set(rows)) != 2 or len(set(cols)) != 2:
                continue

            # avoid squares; # todo unsure if an edge cell is a must, here it is
            vertical_lines = set((col for col in cols if cols.count(col) > 1))
            horizontal_lines = set((row for row in rows if rows.count(row) > 1))
            if len(vertical_lines) != 1 or len(horizontal_lines) != 1:
                continue
            horizontal_line, vertical_line = horizontal_lines.pop(), vertical_lines.pop()

            # find a conjugate pair (a row or column containing only two candidates, one of them being our candidate)
            # where one of the candidates is in the row/col forming the ER.
            # If the col/row of the ER contains a candidate, that can see the second candidate of the conjugate pair,
            # it can be invalidated.
            cells_on_row = horizontal_line.get_cells_having_candidate(candidate=candidate,
                                                                      except_cells=cells)
            cells_on_col = vertical_line.get_cells_having_candidate(candidate=candidate,
                                                                    except_cells=cells)

            # we need a cell on the row/col that build a conjugate pair with another cell on it's col/row
            for cell_on_row in cells_on_row:
                cells_same_col = cell_on_row.column.get_cells_having_candidate(candidate=candidate,
                                                                               except_cells=[cell_on_row])
                if len(cells_same_col) != 1:
                    continue

                # now we try to form a rectangle by checking whether the cell on found cell's
                # row and on the rectangle's col (i.e. at the final angle of the rectangle) has our candidate
                angle_cell = board.get_cell(y=cells_same_col[0].y, x=vertical_line.x)
                if not angle_cell.has_candidate(candidate) or angle_cell in cells:
                    continue

                # at that latest cell, we can invalidate our candidate
                invalidated_cells = [(angle_cell, candidate)]
                default = [(cell.x, cell.y, candidate, IndicatorLevel.DEFAULT) for cell in cells]
                conjugate_pair = [(cell_on_row.x, cell_on_row.y, candidate, IndicatorLevel.ALTERNATIVE),
                                  (cells_same_col[0].x, cells_same_col[0].y, candidate, IndicatorLevel.ALTERNATIVE)]
                empty_rectangle = CommonPreview(invalidated_cells=invalidated_cells,
                                                indicator_candidates=tuple(default + conjugate_pair))
                board.notify_preview(preview=empty_rectangle)
                return

            # todo avoid repeating, this looks really ugy...
            for cell_on_col in cells_on_col:
                cells_same_row = cell_on_col.row.get_cells_having_candidate(candidate=candidate,
                                                                            except_cells=[cell_on_col])
                if len(cells_same_row) != 1:
                    continue

                angle_cell = board.get_cell(x=cells_same_row[0].x, y=horizontal_line.y)
                if not angle_cell.has_candidate(candidate) or angle_cell in cells:
                    continue

                # at that latest cell, we can invalidate our candidate
                invalidated_cells = [(angle_cell, candidate)]
                default = [(cell.x, cell.y, candidate, IndicatorLevel.DEFAULT) for cell in cells]
                conjugate_pair = [(cell_on_col.x, cell_on_col.y, candidate, IndicatorLevel.ALTERNATIVE),
                                  (cells_same_row[0].x, cells_same_row[0].y, candidate, IndicatorLevel.ALTERNATIVE)]
                empty_rectangle = CommonPreview(invalidated_cells=invalidated_cells,
                                                indicator_candidates=tuple(default + conjugate_pair))
                board.notify_preview(preview=empty_rectangle)
                return
