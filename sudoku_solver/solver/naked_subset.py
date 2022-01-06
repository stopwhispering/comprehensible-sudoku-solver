import itertools
from typing import List, Tuple

from sudoku_solver.board.board import Board
from sudoku_solver.board.cell import Cell
from sudoku_solver.board.houses import House
from sudoku_solver.shared.preview import Preview, IndicatorLevel
from sudoku_solver.solver.decorators import evaluate_algorithm


class NakedSubset(Preview):
    def __init__(self,
                 candidates: List[int],
                 naked_cells: List[Cell],  # twin, triple, quadruple, etc.
                 other_cells: List[Cell]):
        self.candidates: List[int] = candidates
        self.naked_cells = naked_cells
        self.other_cells = other_cells

    def get_indicator_candidates(self) -> Tuple[Tuple[int, int, int, IndicatorLevel]]:
        """return the board positions of base row candidates"""
        pos = [(cell.x, cell.y, c, IndicatorLevel.DEFAULT) for cell in self.naked_cells for c in cell.candidates
               if c in self.candidates]
        return tuple(pos)

    def get_invalidated_candidates(self) -> Tuple[Tuple[int, int, int]]:
        """return the board positions where the candidate is invalidated"""
        pos = [(cell.x, cell.y, c) for cell in self.other_cells for c in cell.candidates
               if c in self.candidates]
        return tuple(pos)

    def execute(self):
        invalidate = [(cell, candidate) for cell in self.other_cells for candidate in cell.candidates
                      if candidate in self.candidates]
        for cell, candidate in invalidate:
            cell.flag_candidates_invalid([candidate])


def _identify_naked_subset_in_house(house: House, n_cand: Tuple[int, ...]) -> NakedSubset:
    """if three cells together share the same 3 candidates (although they don't need to have them all),
    then we can rule these candidates out for other cells of the unit. Example:
    (39), (59), (359) -> other cells may not have 359"""
    unfinished_values = house.get_unfinished_values()

    for n in n_cand:
        # get all triple or quadruple combinations of yet unfinished candidates
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


@evaluate_algorithm
def find_naked_subset(board: Board):
    """generalization of naked pair (triples, quadruples, etc.)
    Example: if three cells together share the same 3 candidates (although they don't need to have them all),
    then we can rule these candidates out for other cells of the unit. Example:
    (39), (59), (359) -> other cells may not have 359"""
    for house in board.get_all_houses():
        naked_subset = _identify_naked_subset_in_house(house=house, n_cand=(2, 3, 4, 5,))
        if naked_subset:
            board.notify_preview(preview=naked_subset)
            return


