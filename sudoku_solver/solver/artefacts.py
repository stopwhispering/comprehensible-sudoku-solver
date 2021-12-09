from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Set, Tuple, Protocol, Optional

from sudoku_solver.board.cell import Cell


class IndicatorLevel(Enum):
    FIRST = 'first'
    LAST = 'last'
    DEFAULT = 'default'
    ALTERNATIVE = 'alternative'


class Artefact(Protocol):
    def execute(self) -> None:
        """execute the invalidation of candidates"""

    def get_preview_line_nodes(self) -> Tuple[Tuple[int, int, int]]:  # x, y, candidate
        """get the nodes of a preview line, e.g. from chain start to chain end"""

    def get_invalidated_candidates(self) -> Tuple[Tuple[int, int, int]]:  # x, y, candidate
        """get the candidate positions to be invalidated"""

    def get_indicator_candidates(self) -> Tuple[Tuple[int, int, int, Optional[IndicatorLevel]]]:
        """get candidate positions to be highlighted"""


@dataclass
class XChain(Artefact):
    chain: List[Cell]
    candidate: int
    other_cells_seeing_start_and_end: Set[Cell]

    def get_preview_line_nodes(self) -> Tuple[Tuple[int, int, int]]:
        """create a line from chain start to chain end"""
        # just concatenate the x/y/c combination from start to end
        nodes = tuple((c.x, c.y, self.candidate) for c in self.chain)
        return nodes

    def get_invalidated_candidates(self) -> Tuple[Tuple[int, int, int]]:
        """return the board positions where the candidate is invalidated"""
        positions = tuple((c.x, c.y, self.candidate) for c in self.other_cells_seeing_start_and_end)
        return positions

    def execute(self):
        for cell in self.other_cells_seeing_start_and_end:
            cell.flag_candidates_invalid([self.candidate])


class Skyscraper(Artefact):
    def __init__(self, candidate: int, cells_seeing_both_roof_cells: Set[Cell]):
        self.candidate = candidate
        self.cells_seeing_both_roof_cells = cells_seeing_both_roof_cells

    def get_invalidated_candidates(self) -> Tuple[Tuple[int, int, int]]:
        """return the board positions where the candidate is invalidated"""
        positions = tuple((c.x, c.y, self.candidate) for c in self.cells_seeing_both_roof_cells)
        return positions

    def execute(self):
        for cell in self.cells_seeing_both_roof_cells:
            cell.flag_candidates_invalid([self.candidate])


class NFish(Artefact):
    def __init__(self, candidate: int,
                 cells_in_base_rows_or_columns: List[Cell],
                 other_cells_in_cover_columns_or_rows: List[Cell]):
        self.candidate = candidate
        self.cells_in_base_rows_or_columns = cells_in_base_rows_or_columns
        self.other_cells_in_cover_columns_or_rows = other_cells_in_cover_columns_or_rows

    def get_indicator_candidates(self) -> Tuple[Tuple[int, int, int, IndicatorLevel]]:
        """return the board positions of base row candidates"""
        pos = tuple((c.x, c.y, self.candidate, IndicatorLevel.DEFAULT) for c in self.cells_in_base_rows_or_columns)
        return pos

    def get_invalidated_candidates(self) -> Tuple[Tuple[int, int, int]]:
        """return the board positions where the candidate is invalidated"""
        positions = tuple((c.x, c.y, self.candidate) for c in self.other_cells_in_cover_columns_or_rows)
        return positions

    def execute(self):
        for cell in self.other_cells_in_cover_columns_or_rows:
            cell.flag_candidates_invalid([self.candidate])


class HiddenSubset(Artefact):
    def __init__(self,
                 candidates: List[int],
                 hidden_cells: List[Cell], ):
        self.candidates: List[int] = candidates
        self.hidden_cells = hidden_cells

    def get_indicator_candidates(self) -> Tuple[Tuple[int, int, int, IndicatorLevel]]:
        """return the board positions of base row candidates"""
        pos = [(cell.x, cell.y, c, IndicatorLevel.DEFAULT) for cell in self.hidden_cells for c in cell.possible_values
               if c in self.candidates]
        return tuple(pos)

    def get_invalidated_candidates(self) -> Tuple[Tuple[int, int, int]]:
        """return the board positions where the candidate is invalidated"""
        pos = [(cell.x, cell.y, c) for cell in self.hidden_cells for c in cell.possible_values
               if c not in self.candidates]
        return tuple(pos)

    def execute(self):
        invalidate = [(cell, candidate) for cell in self.hidden_cells for candidate in cell.possible_values
                      if candidate not in self.candidates]
        for cell, candidate in invalidate:
            cell.flag_candidates_invalid([candidate])


class NakedSubset(Artefact):
    def __init__(self,
                 candidates: List[int],
                 naked_cells: List[Cell],  # twin, triple, quadruple, etc.
                 other_cells: List[Cell]):
        self.candidates: List[int] = candidates
        self.naked_cells = naked_cells
        self.other_cells = other_cells

    def get_indicator_candidates(self) -> Tuple[Tuple[int, int, int, IndicatorLevel]]:
        """return the board positions of base row candidates"""
        pos = [(cell.x, cell.y, c, IndicatorLevel.DEFAULT) for cell in self.naked_cells for c in cell.possible_values
               if c in self.candidates]
        return tuple(pos)

    def get_invalidated_candidates(self) -> Tuple[Tuple[int, int, int]]:
        """return the board positions where the candidate is invalidated"""
        pos = [(cell.x, cell.y, c) for cell in self.other_cells for c in cell.possible_values
               if c in self.candidates]
        return tuple(pos)

    def execute(self):
        invalidate = [(cell, candidate) for cell in self.other_cells for candidate in cell.possible_values
                      if candidate in self.candidates]
        for cell, candidate in invalidate:
            cell.flag_candidates_invalid([candidate])


@dataclass
class ChainCell:
    cell: Cell
    starting_candidate: int
    next_candidate: int


class XYChain(Artefact):
    def __init__(self, starting_cell: Cell, starting_candidate: int):
        self.chain: List[ChainCell] = []
        self.other_cells: List[Cell] = []
        self.starting_candidate = starting_candidate
        self.add(starting_cell)

    def __contains__(self, cell: Cell):
        """override in operator"""
        return cell in [c.cell for c in self.chain]

    @property
    def last_cell(self) -> Cell:
        return self.chain[-1].cell

    @property
    def first_cell(self) -> Cell:
        return self.chain[0].cell

    @property
    def required_candidate_for_next_cell(self):
        if self.chain:
            return self.chain[-1].next_candidate
        else:
            return self.starting_candidate

    def add(self, cell):
        assert len(cell.possible_values) == 2
        assert self.required_candidate_for_next_cell in cell.possible_values
        next_candidate = [c for c in cell.possible_values if c != self.required_candidate_for_next_cell][0]
        self.chain.append(ChainCell(cell=cell,
                                    starting_candidate=self.required_candidate_for_next_cell,
                                    next_candidate=next_candidate))

    def pop(self) -> Cell:
        member = self.chain.pop()
        return member.cell

    def is_valid_xy_chain(self) -> bool:
        if len(self.chain) % 2 == 0 and self.chain[0].starting_candidate == self.chain[-1].next_candidate:
            return True
        else:
            return False

    def get_indicator_candidates(self) -> Tuple[Tuple[int, int, int, IndicatorLevel]]:
        positions = []
        first_start = (self.chain[0].cell.x, self.chain[0].cell.y, self.chain[0].starting_candidate,
                       IndicatorLevel.FIRST,)
        first_next = (self.chain[0].cell.x, self.chain[0].cell.y, self.chain[0].next_candidate,
                      IndicatorLevel.DEFAULT,)
        positions.append(first_start)
        positions.append(first_next)

        for member in self.chain:
            positions.append((member.cell.x, member.cell.y, member.starting_candidate, IndicatorLevel.DEFAULT))
            positions.append((member.cell.x, member.cell.y, member.next_candidate, IndicatorLevel.ALTERNATIVE))

        last_start = (self.chain[-1].cell.x, self.chain[-1].cell.y, self.chain[-1].starting_candidate,
                      IndicatorLevel.DEFAULT)
        last_next = (self.chain[-1].cell.x, self.chain[-1].cell.y, self.chain[-1].next_candidate,
                     IndicatorLevel.LAST)
        positions.append(last_start)
        positions.append(last_next)

        return tuple(positions)

    def get_invalidated_candidates(self) -> Tuple[Tuple[int, int, int]]:
        """return the board positions where the candidate is invalidated"""
        positions = tuple((c.x, c.y, self.starting_candidate) for c in self.other_cells)
        return positions

    def execute(self):
        for cell in self.other_cells:
            cell.flag_candidates_invalid([self.starting_candidate])
