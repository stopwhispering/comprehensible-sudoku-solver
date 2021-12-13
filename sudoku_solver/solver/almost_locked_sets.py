import itertools
from collections import defaultdict
from typing import List, Tuple, Sequence, Optional

from sudoku_solver.board.board import Board
from sudoku_solver.board.cell import Cell
from sudoku_solver.board.preview import CommonPreview, IndicatorLevel


def find_almost_locked_sets(board: Board, max_size: int = 3) -> List[Tuple[Cell, ...]]:
    """an almost locked set is a set of n cells within a house that hat n+1 candidates.
    note: if it had n candidates, it would be a naked subset.
    this could very well return > 200 als if we didn't set a max_size"""

    # collect <<all>> als (with 2+ cells)
    als = []
    for house in board.get_all_houses():
        cells = house.get_cells(only_unsolved=True)

        cell_combinations = []
        for length in range(2, min(len(cells) + 1, max_size)):
            cell_combinations.extend(list(itertools.combinations(cells, length)))

        for cell_combination in cell_combinations:
            count_candidates = len(set([candidate for cell in cell_combination for candidate in cell.candidates]))
            if count_candidates == len(cell_combination) + 1 and cell_combination not in als:
                als.append(cell_combination)

    return als


def get_rcc_for_als_combination(board: Board, als_combination: Tuple[Tuple[Cell, ...], ...]) -> Tuple[List[int],
                                                                                                      List[int]]:
    """return restricted common candidates (rcc) (0..n) plus other common candidates (0..n)
    an rcc can be true for only one almost locked set of two"""
    possible_values_a = set([candidate for cell in als_combination[0] for candidate in cell.candidates])
    possible_values_b = set([candidate for cell in als_combination[1] for candidate in cell.candidates])
    common_candidates = possible_values_a.intersection(possible_values_b)
    if not common_candidates:
        return [], []

    rcc = []
    for common_candidate in common_candidates:
        # we only have an rcc, if all cells having that candidate see each other
        cells_a = [cell for cell in als_combination[0] if cell.has_candidate(common_candidate)]
        cells_b = [cell for cell in als_combination[1] if cell.has_candidate(common_candidate)]
        assert cells_a and cells_b

        # cells in both sets may overlap, but not for rcc cells
        if not set(cells_a).isdisjoint(cells_b):
            continue

        if board.are_cell_sets_seeing_each_other(candidate=common_candidate, cells_a=cells_a, cells_b=cells_b):
            rcc.append(common_candidate)

    other_common_candidates = [c for c in common_candidates if c not in rcc]
    return rcc, other_common_candidates


def _check_singly_linked_als(board: Board,
                             als_combination: Tuple[Tuple[Cell, ...]],
                             rcc: int,
                             other_common_candidate: int) -> Optional[CommonPreview]:
    # we can not invalidate the other common candidate from all non-als cells that see the als-cells having
    # the common candidate
    # other_common_candidate =
    als_cells = [cell for als in als_combination for cell in als if cell.has_candidate(
            candidate=other_common_candidate)]
    other_cells = board.get_cells_seeing_all_supplied_cells(candidate=other_common_candidate, cells=als_cells)
    if not other_cells:
        return None

    invalidated_cells = [(cell, other_common_candidate) for cell in other_cells]
    indicator_candidates = []
    for cell in als_combination[0] + als_combination[1]:
        for candidate in cell.candidates:
            if candidate == rcc:
                indicator_candidates.append((cell.x, cell.y, candidate, IndicatorLevel.ALTERNATIVE))
            elif candidate == other_common_candidate:
                indicator_candidates.append((cell.x, cell.y, candidate, IndicatorLevel.LAST))
            else:
                indicator_candidates.append((cell.x, cell.y, candidate, IndicatorLevel.DEFAULT))

    singly_linked_als = CommonPreview(invalidated_cells=invalidated_cells,
                                      indicator_candidates=tuple(indicator_candidates))
    return singly_linked_als


def _check_doubly_linked_als(board: Board,
                             als_combination: Tuple[Tuple[Cell, ...]],
                             rcc: Sequence[int]) -> Optional[CommonPreview]:
    invalidate_cells = defaultdict(list)
    for rcc_candidate in rcc:
        cells = [cell for cells in als_combination for cell in cells if cell.has_candidate(rcc_candidate)]
        shared_houses = board.get_houses_shared_by_cells(cells=cells)

        # get other cells having the rcc in the houses
        for shared_house in shared_houses:
            invalidate = shared_house.get_cells_having_candidate(candidate=rcc_candidate, except_cells=cells)
            if invalidate:
                invalidate_cells[rcc_candidate].extend(invalidate)

    if invalidate_cells:
        invalidated_cells = []
        for key, value in invalidate_cells.items():
            for cell in set(value):
                invalidated_cells.append((cell, key))

        indicator_candidates = []
        for cell in als_combination[0] + als_combination[1]:
            for candidate in cell.candidates:
                if candidate in rcc:
                    indicator_candidates.append((cell.x, cell.y, candidate, IndicatorLevel.ALTERNATIVE))
                else:
                    indicator_candidates.append((cell.x, cell.y, candidate, IndicatorLevel.DEFAULT))

        doubly_linked_als = CommonPreview(invalidated_cells=invalidated_cells,
                                          indicator_candidates=tuple(indicator_candidates))
        return doubly_linked_als


def find_singly_or_doubly_linked_als(board: Board):
    als = find_almost_locked_sets(board=board)

    # get each possible combination of two als
    als_combinations = list(itertools.combinations(als, 2))

    # for each combination of two als, check whether we have a restricted common candidate (RCC), i.e.
    # a candidate that is available in both als with the cells having the candidate in one als seeing all cells
    # having the candidate in the other als (and the other way around)
    for als_combination in als_combinations:

        rcc, other_common_candidates = get_rcc_for_als_combination(board=board, als_combination=als_combination)

        if len(rcc) == 1 and other_common_candidates:  # and len(other_common_candidates) == 1:
            singly_linked_als = _check_singly_linked_als(board=board,
                                                         als_combination=als_combination,
                                                         rcc=rcc[0],
                                                         other_common_candidate=other_common_candidates[0])
            if singly_linked_als:
                board.notify_preview(preview=singly_linked_als)
                return

        elif len(rcc) == 2:
            doubly_linked_als = _check_doubly_linked_als(board=board,
                                                         als_combination=als_combination,
                                                         rcc=rcc)
            if doubly_linked_als:
                board.notify_preview(preview=doubly_linked_als)
                return
