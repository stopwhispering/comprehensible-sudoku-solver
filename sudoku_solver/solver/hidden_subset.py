import itertools
from typing import Optional, Sequence

from sudoku_solver.board.board import Board
from sudoku_solver.board.cell import Cell
from sudoku_solver.board.houses import House
from sudoku_solver.shared.preview import Preview, IndicatorLevel, HighlightedPosition
from sudoku_solver.shared.puzzle import ValuePosition
from sudoku_solver.solver.decorators import evaluate_algorithm


class HiddenSubset(Preview):
    def __init__(self,
                 candidates: Sequence[int],
                 hidden_cells: Sequence[Cell], ):
        self.candidates = candidates
        self.hidden_cells = hidden_cells

    def get_indicator_candidates(self) -> Sequence[HighlightedPosition]:
        """return the board positions of base row candidates"""
        pos = [HighlightedPosition(x=cell.x, y=cell.y, value=c, indicator_level=IndicatorLevel.DEFAULT) for cell in
               self.hidden_cells for c in cell.candidates if c in self.candidates]
        return pos

    def get_invalidated_candidates(self) -> Sequence[ValuePosition]:
        """return the board positions where the candidate is invalidated"""
        return tuple((ValuePosition(x=cell.x, y=cell.y, value=c) for cell in self.hidden_cells for c in cell.candidates
                      if c not in self.candidates))

    def execute(self):
        invalidate = [(cell, candidate) for cell in self.hidden_cells for candidate in cell.candidates
                      if candidate not in self.candidates]
        for cell, candidate in invalidate:
            cell.flag_candidates_invalid([candidate])


def identify_hidden_subset_in_house(house: House) -> Optional[HiddenSubset]:
    """if three candidate candidates are valid for only three cells (although they
    don't need to each have all of them),
    then we can rule out all other candidate candidates for these cells. Example:
    123 are candidates for only 1357, 1259, 2357 -> make them 13, 12, 23"""
    unfinished_values = house.get_unfinished_values()

    for n in (2, 3, 4, 5,):
        # get all triple combinations of yet unfinished candidates
        # find out if there's exactly three cells that have any of them as candidates
        value_combinations = tuple(itertools.combinations(unfinished_values, n))
        for value_combination in value_combinations:
            cells = house.get_cells_having_any_of_candidates(value_combination)
            invalidate = [candidate for cell in cells for candidate in cell.candidates
                          if candidate not in value_combination]
            if len(cells) == n and invalidate:
                hidden_subset = HiddenSubset(candidates=value_combination, hidden_cells=cells)
                return hidden_subset


@evaluate_algorithm
def find_hidden_subset(board: Board):
    """if three candidate candidates are valid for only three cells (although they
    don't need to each have all of them),
    then we can rule out all other candidate candidates for these cells. Example:
    123 are candidates for only 1357, 1259, 2357 -> make them 13, 12, 23"""
    for house in board.get_all_houses():
        hidden_subset = identify_hidden_subset_in_house(house=house)
        if hidden_subset:
            board.notify_preview(preview=hidden_subset)
            return
