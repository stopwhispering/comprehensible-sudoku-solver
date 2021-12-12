from sudoku_solver.board.board import Board
from sudoku_solver.board.houses import House, Block, Column, Row
from sudoku_solver.board.preview import CommonPreview, IndicatorLevel


def _find_locked_candidate_in_house(house: House) -> CommonPreview:
    unfinished_candidates = house.get_unfinished_values()

    for candidate in unfinished_candidates:

        cells_with_candidate = house.get_cells_having_candidate(candidate=candidate)
        if len(cells_with_candidate) < 2:
            continue

        other_cells = []
        if isinstance(house, Block):
            if house.cells_in_same_row(cells=cells_with_candidate):
                other_cells = cells_with_candidate[0].row.get_cells_having_candidate(candidate=candidate,
                                                                                     except_cells=cells_with_candidate)
            elif house.cells_in_same_col(cells=cells_with_candidate):
                other_cells = cells_with_candidate[0].column.get_cells_having_candidate(
                        candidate=candidate,
                        except_cells=cells_with_candidate)
        elif isinstance(house, Row) or isinstance(house, Column):
            if house.cells_in_same_block(cells=cells_with_candidate):
                other_cells = cells_with_candidate[0].block.get_cells_having_candidate(
                        candidate=candidate,
                        except_cells=cells_with_candidate)

        if other_cells:
            invalidated_cells = [(cell, candidate) for cell in other_cells]
            indicator_candidates = ((c.x, c.y, candidate, IndicatorLevel.DEFAULT) for c in cells_with_candidate)
            locked_candidate = CommonPreview(invalidated_cells=invalidated_cells,
                                             indicator_candidates=tuple(indicator_candidates))
            return locked_candidate


def find_locked_candidate(board: Board):
    """in a house, look for all cells having a specific candidate
       a. if we're in a box, test if all these cells are in a single row or column
       b. if we're in a row/col, test if all these cells are in a single box
    if true, we can invalidate that candidate for...
       a. other cells in that row or column
       b. other cells in that box
    """
    for house in board.get_all_houses():
        locked_candidate = _find_locked_candidate_in_house(house=house)
        if locked_candidate:
            board.notify_preview(preview=locked_candidate)
            return