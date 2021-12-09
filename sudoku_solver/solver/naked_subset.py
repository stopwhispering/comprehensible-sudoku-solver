import itertools

from sudoku_solver.board.board import Board
from sudoku_solver.board.houses import House
from sudoku_solver.solver.artefacts import NakedSubset


def identify_naked_subset_in_house(house: House) -> NakedSubset:
    """if three cells together share the same 3 candidates (although they don't need to have them all),
    then we can rule these candidates out for other cells of the unit. Example:
    (39), (59), (359) -> other cells may not have 359"""
    unfinished_values = house.get_unfinished_values()

    for n in (2, 3, 4, 5,):
        # get all triple or quadruple combinations of yet unfinished values
        # find out if there's exactly three cells that have <<only>> them as candidates
        value_combinations = tuple(itertools.combinations(unfinished_values, n))
        for value_combination in value_combinations:
            cells = house.get_cells_having_only_candidates(value_combination)
            if len(cells) == n:
                for value in value_combination:
                    other_cells = [c for c in house.get_cells_having_candidate(value) if c not in cells]

                    if other_cells:
                        naked_pair = NakedSubset(candidates=list(value_combination),
                                                 naked_cells=cells,
                                                 other_cells=other_cells)
                        return naked_pair


def find_naked_subset(board: Board):
    """generalization of naked pair (triples, quadruples, etc.)"""
    for house in board.get_all_houses():
        naked_subset = identify_naked_subset_in_house(house=house)
        if naked_subset:
            board.notify_preview(preview=naked_subset)
            return
