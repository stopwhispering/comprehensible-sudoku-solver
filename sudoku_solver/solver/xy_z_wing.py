import itertools

from sudoku_solver.board.board import Board
from sudoku_solver.shared.preview import IndicatorLevel, CommonPreview, HighlightedPosition
from sudoku_solver.solver.decorators import evaluate_algorithm


@evaluate_algorithm
def find_xy_wing(board: Board):
    """Starting with a cell ("pivot") that has two candidates ("X" and "Y"), we look out for two another
    cells ("Pincers") with two candidates each: X+Z and Y+Z, Z being any other candidate. Both pincer cells may not
    be in the same house (cf. naked triple). As either one or both of the pincers have candidate Z, we may invalidate Z
    from all other cells seeing both pincer cells."""
    # start with a cell that has 2 candidates
    starting_cells = board.get_cells_by_number_of_candidates(n_candidates=2)
    for pivot_cell in starting_cells:
        candidate_x, candidate_y = pivot_cell.candidates

        # find pincer cells
        pincers_x = pivot_cell.seen_by(candidate=candidate_x, n_candidates=2)
        pincers_y = pivot_cell.seen_by(candidate=candidate_y, n_candidates=2)

        # for each combination of pincer_x and pincer_y, check if they fulfill the conditions...
        pincer_combinations = itertools.product(pincers_x, pincers_y)
        for pincer_combination in pincer_combinations:

            # both pincer cells must have a common candidate Z
            candidate_z = [c for c in pincer_combination[0].candidates if c != candidate_x][0]
            candidate_z_b = [c for c in pincer_combination[1].candidates if c != candidate_y][0]
            if candidate_z != candidate_z_b:
                continue

            # both pincer cells must be in different houses
            if pincer_combination[0].block is pincer_combination[1].block:
                continue

            # we may now invalidate Z in all other cells seeing both pincers
            seen_by_pincers = board.get_cells_seeing_both_supplied_cells(candidate=candidate_z,
                                                                         cell_a=pincer_combination[0],
                                                                         cell_b=pincer_combination[1])
            if seen_by_pincers:
                invalidated_cells = [(cell, candidate_z) for cell in seen_by_pincers]
                indicator_candidates = (
                    HighlightedPosition(pivot_cell.x, pivot_cell.y, candidate_x, IndicatorLevel.DEFAULT),
                    HighlightedPosition(pivot_cell.x, pivot_cell.y, candidate_y, IndicatorLevel.DEFAULT),
                    HighlightedPosition(pincer_combination[0].x, pincer_combination[0].y, candidate_x,
                                        IndicatorLevel.DEFAULT),
                    HighlightedPosition(pincer_combination[0].x, pincer_combination[0].y, candidate_z,
                                        IndicatorLevel.ALTERNATIVE),
                    HighlightedPosition(pincer_combination[1].x, pincer_combination[1].y, candidate_y,
                                        IndicatorLevel.DEFAULT),
                    HighlightedPosition(pincer_combination[1].x, pincer_combination[1].y, candidate_z,
                                        IndicatorLevel.ALTERNATIVE),
                    )
                xy_wing = CommonPreview(invalidated_cells=invalidated_cells,
                                        indicator_candidates=indicator_candidates)
                board.notify_preview(preview=xy_wing)
                return


@evaluate_algorithm
def find_xyz_wing(board: Board):
    """Starting with a cell ("pivot") that has three candidates ("X", "Y", "Z"), we look out for two another
    cells ("Pincers") with two candidates each: X+Z and Y+Z. Both pincer cells may not
    be in the same house (cf. naked triple). We may then invalidate Z from all other cells seeing all the three cells.
    cf. XY-Wing where Z is not a candidate of the pivot cell."""
    # start with a cell that has 3 candidates
    starting_cells = board.get_cells_by_number_of_candidates(n_candidates=3)
    for pivot_cell in starting_cells:

        # we'll test all three candidates as Z
        for candidate_z in pivot_cell.candidates:

            candidate_x, candidate_y = [c for c in pivot_cell.candidates if c != candidate_z]

            # find pincer cells
            pincers_x = pivot_cell.seen_by_with_exact_candidates(candidates=[candidate_x, candidate_z])
            pincers_y = pivot_cell.seen_by_with_exact_candidates(candidates=[candidate_y, candidate_z])

            if not pincers_x or not pincers_y:
                continue

            # for each combination of pincer_x and pincer_y, check if they fulfill the conditions...
            pincer_combinations = itertools.product(pincers_x, pincers_y)
            for pincer_combination in pincer_combinations:

                # both pincer cells must be in different houses
                if pincer_combination[0].block is pincer_combination[1].block:
                    continue

                # we may now invalidate Z in all other cells seeing both pincers and the pivot cell
                all_three = [pincer_combination[0], pincer_combination[1], pivot_cell]
                seen_by_all_three = board.get_cells_seeing_all_supplied_cells(candidate=candidate_z,
                                                                              cells=all_three)

                if seen_by_all_three:
                    invalidated_cells = [(cell, candidate_z) for cell in seen_by_all_three]
                    indicator_candidates = (
                        HighlightedPosition(pivot_cell.x, pivot_cell.y, candidate_x, IndicatorLevel.DEFAULT),
                        HighlightedPosition(pivot_cell.x, pivot_cell.y, candidate_y, IndicatorLevel.DEFAULT),
                        HighlightedPosition(pivot_cell.x, pivot_cell.y, candidate_z, IndicatorLevel.ALTERNATIVE),
                        HighlightedPosition(pincer_combination[0].x, pincer_combination[0].y, candidate_x,
                                            IndicatorLevel.DEFAULT),
                        HighlightedPosition(pincer_combination[0].x, pincer_combination[0].y, candidate_z,
                                            IndicatorLevel.ALTERNATIVE),
                        HighlightedPosition(pincer_combination[1].x, pincer_combination[1].y, candidate_y,
                                            IndicatorLevel.DEFAULT),
                        HighlightedPosition(pincer_combination[1].x, pincer_combination[1].y, candidate_z,
                                            IndicatorLevel.ALTERNATIVE),
                        )
                    xy_wing = CommonPreview(invalidated_cells=invalidated_cells,
                                            indicator_candidates=indicator_candidates)
                    board.notify_preview(preview=xy_wing)
                    return
