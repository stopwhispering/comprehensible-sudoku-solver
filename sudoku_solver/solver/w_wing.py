import itertools

from sudoku_solver.board.board import Board
from sudoku_solver.shared.preview import IndicatorLevel, CommonPreview
from sudoku_solver.solver.decorators import evaluate_algorithm


@evaluate_algorithm
def find_w_wing(board: Board):
    """W-Wing Strategy"""
    # find combinations of two cells, both having the same two candidates ("W" and "Z"); both cells may not be in
    # the same house

    cells_with_two_candidates = board.get_cells_by_number_of_candidates(n_candidates=2)
    candidate_pairs = [tuple(cell.candidates) for cell in cells_with_two_candidates]
    candidate_pairs_two_plus = set([p for p in candidate_pairs if candidate_pairs.count(p) >= 2])
    reverse = set([(c[1], c[0]) for c in candidate_pairs_two_plus])
    # we will try first/second candidate for w/z candidate. so we need to permutate the combinations.
    # e.g. {(5,7),(1,2)} -> {(5,7),(1,2),(7,5),(2,1)}
    for candidate_combination in set.union(candidate_pairs_two_plus, reverse):
        candidate_w, candidate_z = candidate_combination
        cells = board.get_cells_by_exact_candidates(candidates=candidate_combination)
        assert len(cells) >= 2

        cell_combinations = tuple(itertools.combinations(cells, 2))
        for pincer_cells in cell_combinations:
            if board.are_cells_in_same_house(cells=pincer_cells):
                continue

            # look for more cells with candidate "W" (and other candidates)
            w_cells_all = board.get_cells_by_candidate(candidate=candidate_w, except_cells=pincer_cells)

            # we need two W-Cells (Pivot Cells), one of the W-Cells must be in house of pincer cell 1, the other
            # in house of pincer cell 2
            # the two pivot cells must be in the same house and must be the only cells having candidate W in that house
            w_cells_a = [c for c in w_cells_all
                         if c.is_seen_by_cell(pincer_cells[0]) and not c.is_seen_by_cell(pincer_cells[1])]
            w_cells_b = [c for c in w_cells_all
                         if c.is_seen_by_cell(pincer_cells[1]) and not c.is_seen_by_cell(pincer_cells[0])]

            w_cells_combinations = tuple(itertools.product(w_cells_a, w_cells_b))
            for pivot_cells in w_cells_combinations:
                shared_houses = board.get_common_houses(cells=pivot_cells)

                # cells might be both in same row/col and same block
                # test if a house has W nly in the pivot cells
                houses = [h for h in shared_houses if len(h.get_cells_having_candidate(candidate=candidate_w)) == 2]
                if not houses:
                    continue

                # we found a w-wing. we may now invalidate candidate <<Z>> (not W!) in all cells seeing both pincer
                # cells
                other_cells = board.get_cells_seeing_all_supplied_cells(candidate=candidate_z, cells=pincer_cells)

                if other_cells:
                    invalidated_cells = [(cell, candidate_z) for cell in other_cells]
                    indicator_candidates = []
                    for pincer_cell in pincer_cells:
                        indicator_candidates.append((pincer_cell.x, pincer_cell.y, candidate_w, IndicatorLevel.DEFAULT))
                        indicator_candidates.append(
                                (pincer_cell.x, pincer_cell.y, candidate_z, IndicatorLevel.ALTERNATIVE))
                    for pivot_cell in pivot_cells:
                        indicator_candidates.append((pivot_cell.x, pivot_cell.y, candidate_w, IndicatorLevel.DEFAULT))
                    w_wing = CommonPreview(invalidated_cells=invalidated_cells,
                                           indicator_candidates=tuple(indicator_candidates))
                    board.notify_preview(preview=w_wing)
                    return
