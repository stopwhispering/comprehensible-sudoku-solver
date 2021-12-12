import itertools
from typing import Optional

from sudoku_solver.board.board import Board
from sudoku_solver.board.houses import Block, HouseType, House
from sudoku_solver.board.preview import Preview, IndicatorLevel, CommonPreview


def _find_sue_de_coq_in_intersection(board: Board,
                                     block: Block,
                                     crossing_house: House) -> Optional[Preview]:
    intersection = block.get_unsolved_intersection_with_other_house(other_house=crossing_house)
    if len(intersection) < 2:
        return

    # do we have three non-solved cells with 5 distinct candidates or three non-solved cells with 4 distinct
    # candidates...
    intersection_candidates = board.get_distinct_candidates(cells=intersection)
    if not ((len(intersection) == 3 and len(intersection_candidates) == 5) or
            (len(intersection) == 2 and len(intersection_candidates) == 4)):
        return

    # find bi-value cells in block and row/column
    block_other_cells = block.get_cells_having_only_candidates(candidates=intersection_candidates,
                                                               except_cells=intersection,
                                                               n_candidates=2)
    crossing_other_cells = crossing_house.get_cells_having_only_candidates(candidates=intersection_candidates,
                                                                           except_cells=intersection,
                                                                           n_candidates=2)
    if not block_other_cells or not crossing_other_cells:
        return

    # we may have multiple combinations
    other_cell_combinations = tuple(itertools.product(block_other_cells, crossing_other_cells))
    for cell_block, cell_other_house in other_cell_combinations:
        assert all(c in intersection_candidates for c in cell_block.candidates)
        assert all(c in intersection_candidates for c in cell_other_house.candidates)
        if not set(cell_block.candidates).isdisjoint(cell_other_house.candidates):
            continue

        # invalidate the two block-cell-candidates from the rest of the cells in the block (except intersection cells).
        cells_block = block.get_cells_having_any_of_candidates(candidates=cell_block.candidates,
                                                               except_cells=intersection + (cell_block,))
        inv_block = [(cell, c) for cell in cells_block for c in cell.candidates if c in cell_block.candidates]
        # invalidate the two row-cell-candidates from the rest of the cells in the row (except intersection cells)
        cells_other = crossing_house.get_cells_having_any_of_candidates(candidates=cell_other_house.candidates,
                                                                        except_cells=intersection + (cell_other_house,))
        inv_other = [(cell, c) for cell in cells_other for c in cell.candidates if c in cell_other_house.candidates]

        #  we may also invalidate any intersection candidate (the 4/5 candidates) that is left (i.e. in neither bi-value
        #  cells) from both the row and the block (but not from the intersection)
        inv_not_bivalue = []
        bivalue_candidates = cell_block.candidates + cell_other_house.candidates
        not_used_intersection_candidates = [c for c in intersection_candidates if c not in bivalue_candidates]
        for c in not_used_intersection_candidates:
            for h in (block, crossing_house):
                cells = h.get_cells_having_candidate(candidate=c, except_cells=intersection)
                inv_not_bivalue += [(cell, c) for cell in cells]

        invalidated_cells = tuple(inv_block + inv_other + inv_not_bivalue)
        if not invalidated_cells:
            continue

        indicator_candidates = []
        for cell in intersection:
            indicator_candidates.extend([(cell.x, cell.y, c, IndicatorLevel.DEFAULT) for c in cell.candidates])
        indicator_candidates.extend(
                [(cell_block.x, cell_block.y, c, IndicatorLevel.ALTERNATIVE) for c in cell_block.candidates])
        indicator_candidates.extend([(cell_other_house.x, cell_other_house.y, c, IndicatorLevel.ALTERNATIVE) for c in
                                     cell_other_house.candidates])

        sue_de_coq = CommonPreview(invalidated_cells=invalidated_cells,
                                   indicator_candidates=tuple(indicator_candidates))
        return sue_de_coq


def find_sue_de_coq(board: Board):
    """we look at each intersection (3 cells) of a block and a row/col:
    - we need either two cells containing (together) 4 distinct candidates or
        three cells containing (together) 5 distinct candidates
    - now we need to find two bi-value cells:
        a. one in the row/col outside of the intersection/block
        b. one in the block outside of the intersection/row/col
    - the two bi-value cells' candidates must be drawn entirely from the
        4/5 candidates above
    - the two bi-value cells must have disjunct candidates
    We may then invalidate the two row cell candidates from the rest of the cells in the row (except intersection cells)
    and invalidate the two block cell candidates from the rest of the cells in the block (except intersection cells).
    We may also invalidate any intersection candidate (the 4/5 candidates) that is left (i.e. in neither bi-value
    cells) from both the row and the block (but not from the intersection).
    """
    blocks = board.get_all_houses(house_type=HouseType.BLOCK)
    for block in blocks:
        block: Block
        # get crossing columns and rows and try out each combination
        crossing_houses = block.get_crossing_houses()
        for crossing_house in crossing_houses:
            preview = _find_sue_de_coq_in_intersection(board=board, block=block, crossing_house=crossing_house)
            if preview:
                board.notify_preview(preview=preview)
                return
