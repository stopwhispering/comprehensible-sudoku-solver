import itertools

from sudoku_solver.board.board import Board
from sudoku_solver.board.preview import CommonPreview, IndicatorLevel, Preview


def _find_unique_rectangles_type_1(board: Board) -> Preview:
    """
    Uniqueness Test Type 1 - One of the four cells of a UR has additional candidates -> UR candidates can be
    eliminated from that cell.
    """
    # find a combination of four cells, each having at least the same two candidates; three of them may <<only>> have
    # these candidates
    cells_two_valued = board.get_cells_by_number_of_candidates(n_candidates=2)
    candidate_combinations_all = [cell.candidates for cell in cells_two_valued]
    candidate_combinations = set([tuple(combi) for combi in candidate_combinations_all if
                                  candidate_combinations_all.count(combi) >= 3])

    # for each unique combination of two candidates (that has 3+ two-valued cells), we test the other requirements
    for candidates in candidate_combinations:
        cells_with_two_candidates = board.get_cells_by_exact_candidates(candidates=candidates)
        cells_with_candidates = board.get_cells_having_candidates(candidates=candidates)
        cells_with_more_candidates = [c for c in cells_with_candidates if len(c.candidates) > 2]

        # test each combination of three two-valued cells and one more-valued cells
        cell_combinations_two_candidates = tuple(itertools.combinations(cells_with_two_candidates, 3))
        combinations = tuple(itertools.product(cell_combinations_two_candidates, cells_with_more_candidates))
        for combination in combinations:
            combi_flat = [c for c in combination[0]] + [combination[1]]
            rows = set((c.row for c in combi_flat))
            cols = set((c.column for c in combi_flat))
            blocks = set((c.block for c in combi_flat))
            if not (len(rows) == len(cols) == len(blocks) == 2):
                continue

            # we may now invalidate the two unique rectangle candidates from the cell that has more than candidates
            invalidated_cells = tuple((combination[1], candidate,) for candidate in candidates)
            default = [(cell.x, cell.y, c, IndicatorLevel.DEFAULT) for cell in combination[0] for c in candidates]
            other_candidates = [c for c in combination[1].candidates if c not in candidates]
            altern = [(combination[1].x, combination[1].y, c, IndicatorLevel.ALTERNATIVE) for c in other_candidates]

            ur_type_1 = CommonPreview(invalidated_cells=invalidated_cells,
                                      indicator_candidates=tuple(default + altern))
            return ur_type_1


def _find_unique_rectangles_type_2(board: Board) -> Preview:
    """
    Uniqueness Test Type 2 - Two of the four cells of a UR have only one, common additional candidate; these two
    cells must be in the same row or column -> any cell seeing these cells for the extra candidate cannot have that
    candidate
    """
    cells_two_valued = board.get_cells_by_number_of_candidates(n_candidates=2)
    candidate_combinations_all = [cell.candidates for cell in cells_two_valued]
    candidate_combinations = set([tuple(combi) for combi in candidate_combinations_all if
                                  candidate_combinations_all.count(combi) >= 2])

    # for each unique combination of two candidates (that has 2+ two-valued cells), we test the other requirements
    for candidates in candidate_combinations:
        cells_two_candidates = board.get_cells_by_exact_candidates(candidates=candidates)
        assert len(cells_two_candidates) >= 2
        cells_with_one_more_candidate = board.get_cells_having_candidates(candidates=candidates, n_candidates=3)
        if len(cells_with_one_more_candidate) < 2:
            continue
        extra_candidates = [c for cell in cells_with_one_more_candidate for c in cell.candidates if c not in candidates]
        extra_candidates_min_two = [c for c in extra_candidates if extra_candidates.count(c) >= 2]
        extra_candidates_distinct = set(extra_candidates_min_two)
        if not extra_candidates_distinct:
            continue

        # test each combination of two two-valued cells with each combination of two three-valued cells having same
        # extra candidate
        cell_combinations_two_candidates = tuple(itertools.combinations(cells_two_candidates, 2))
        for extra_candidate in extra_candidates_distinct:
            cells_three_candidates = [c for c in cells_with_one_more_candidate if c.has_candidate(extra_candidate)]
            assert len(cells_three_candidates) >= 2
            cell_combinations_three_candidates_raw = tuple(itertools.combinations(cells_three_candidates, 2))

            # only those three-candidate combinations are valid where both cells share a row or column
            cell_combinations_three_candidates = [combi for combi in cell_combinations_three_candidates_raw if combi[
                0].row is combi[1].row or combi[0].column is combi[1].column]

            if not cell_combinations_three_candidates:
                continue

            # combine each group of two two-valued with each group of three-valued cells
            combinations = tuple(
                itertools.product(cell_combinations_two_candidates, cell_combinations_three_candidates))
            for combination in combinations:
                combi_flat = [c for c in combination[0]] + [c for c in combination[1]]
                rows = set((c.row for c in combi_flat))
                cols = set((c.column for c in combi_flat))
                blocks = set((c.block for c in combi_flat))
                if not (len(rows) == len(cols) == len(blocks) == 2):
                    continue

                # we may now invalidate any cell seeing the three-candidate cells for the extra candidate
                seen_cells = board.get_cells_seeing_all_supplied_cells(candidate=extra_candidate,
                                                                       cells=combination[1])
                if not seen_cells:
                    continue

                invalidated_cells = tuple((cell, extra_candidate) for cell in seen_cells)
                default = [(cell.x, cell.y, c, IndicatorLevel.DEFAULT) for cell in combi_flat for c in
                           candidates]
                altern = [(cell.x, cell.y, extra_candidate, IndicatorLevel.ALTERNATIVE) for cell in combination[1]]
                ur_type_2 = CommonPreview(invalidated_cells=invalidated_cells,
                                          indicator_candidates=tuple(default + altern))
                return ur_type_2


def _find_unique_rectangles_type_4(board: Board) -> Preview:
    """
    once again look at additional candidates in two non diagonal cells (cf. type II; here, they don't need to match,
    though). If one of the UR  candidates
    is not possible anymore in any other cell of a house that contains both cells with the extra candidates,
    the other UR candidate can be eliminated from those UR cells.
    """
    cells_two_valued = board.get_cells_by_number_of_candidates(n_candidates=2)
    candidate_combinations_all = [cell.candidates for cell in cells_two_valued]
    candidate_combinations = set([tuple(combi) for combi in candidate_combinations_all if
                                  candidate_combinations_all.count(combi) >= 2])

    # for each unique combination of two candidates (that has 2+ two-valued cells), we test the other requirements
    for candidates in candidate_combinations:

        # find cells with the two candidates plus any number (1+) of additional candidates
        cells_two_candidates = board.get_cells_by_exact_candidates(candidates=candidates)
        assert len(cells_two_candidates) >= 2
        cells_with_candidates = board.get_cells_having_candidates(candidates=candidates)
        cells_with_n_more_candidates = [c for c in cells_with_candidates if len(c.candidates) > 2]
        if len(cells_with_n_more_candidates) < 2:
            continue

        # test each combination of two two-valued cells with each combination of two three+-valued cells
        cell_combinations_two = tuple(itertools.combinations(cells_two_candidates, 2))
        cell_combinations_n_raw = tuple(itertools.combinations(cells_with_n_more_candidates, 2))

        # only those three+-candidate combinations are valid where both cells share a row or column
        cell_combinations_n = [combi for combi in cell_combinations_n_raw if combi[
            0].row is combi[1].row or combi[0].column is combi[1].column]

        if not cell_combinations_n:
            continue

        # combine each group of two two-valued with each group of three+-valued cells
        combinations = tuple(itertools.product(cell_combinations_two, cell_combinations_n))
        for combination in combinations:
            combi_flat = [c for c in combination[0]] + [c for c in combination[1]]
            rows = set((c.row for c in combi_flat))
            cols = set((c.column for c in combi_flat))
            blocks = set((c.block for c in combi_flat))
            if not (len(rows) == len(cols) == len(blocks) == 2):
                continue

            # consider the cells seeing both three+-cells (i.e. in same row/col and block): if those other cells
            # don't see one of the UR candidates, then we may invalidate the other UR candidate for both three+-cells.
            for cand in candidates:

                shared_houses = board.get_houses_shared_by_cells(cells=combination[1])
                for house in shared_houses:
                    cells_seeing_both = house.get_cells_having_candidate(candidate=cand,
                                                                         except_cells=combination[1])
                    if not cells_seeing_both:
                        #  we may now invalidate the other UR candidate for both three+-cells.
                        invalid_candidate = candidates[0] if cand == candidates[1] else candidates[1]
                        invalidated_cells = tuple((cell, invalid_candidate) for cell in combination[1])

                        default_two = [(cell.x, cell.y, c, IndicatorLevel.DEFAULT) for cell in combination[0] for c in
                                       candidates]
                        default_n = [(cell.x, cell.y, cand, IndicatorLevel.DEFAULT) for cell in combination[1]]
                        ur_type_4 = CommonPreview(invalidated_cells=invalidated_cells,
                                                  indicator_candidates=tuple(default_two + default_n))
                        return ur_type_4


def find_uniqueness_violations(board: Board):
    """
    A UR (which would be a "bug" in the sudoku making it have multiple solutions) consists of
    four cells that occupy exactly two rows, two columns, and two blocks. All four cells have the same two candidates.
    """
    # todo
    # uniqueness_violation = _find_unique_rectangles_type_1(board=board)
    # if uniqueness_violation:
    #     board.notify_preview(preview=uniqueness_violation)
    #     return
    # uniqueness_violation = _find_unique_rectangles_type_2(board=board)
    # if uniqueness_violation:
    #     board.notify_preview(preview=uniqueness_violation)
    #     return
    uniqueness_violation = _find_unique_rectangles_type_4(board=board)
    if uniqueness_violation:
        board.notify_preview(preview=uniqueness_violation)
        return
