import itertools
from typing import Optional

from sudoku_solver.board.board import Board
from sudoku_solver.board.houses import House
from sudoku_solver.solver.artefacts import HiddenSubset


def identify_hidden_subset_in_house(house: House) -> Optional[HiddenSubset]:
    """if three candidate values are valid for only three cells (although they
    don't need to each have all of them),
    then we can rule out all other candidate values for these cells. Example:
    123 are candidates for only 1357, 1259, 2357 -> make them 13, 12, 23"""
    unfinished_values = house.get_unfinished_values()

    for n in (2, 3, 4, 5,):
        # get all triple combinations of yet unfinished values
        # find out if there's exactly three cells that have any of them as candidates
        value_combinations = tuple(itertools.combinations(unfinished_values, n))
        for value_combination in value_combinations:
            cells = house.get_cells_having_any_of_candidates(value_combination)
            invalidate = [candidate for cell in cells for candidate in cell.possible_values
                          if candidate not in value_combination]
            if len(cells) == n and invalidate:
                hidden_subset = HiddenSubset(candidates=value_combination, hidden_cells=cells)
                return hidden_subset


def find_hidden_subset(board: Board):
    """if three candidate values are valid for only three cells (although they
    don't need to each have all of them),
    then we can rule out all other candidate values for these cells. Example:
    123 are candidates for only 1357, 1259, 2357 -> make them 13, 12, 23"""
    for house in board.get_all_houses():
        hidden_subset = identify_hidden_subset_in_house(house=house)
        if hidden_subset:
            board.notify_preview(preview=hidden_subset)
            return
