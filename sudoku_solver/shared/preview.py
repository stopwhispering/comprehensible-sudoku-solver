from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Protocol, Optional, Sequence

from sudoku_solver.board.cell import Cell
from sudoku_solver.shared.puzzle import ValuePosition


class IndicatorLevel(Enum):
    FIRST = 'first'
    LAST = 'last'
    DEFAULT = 'default'
    ALTERNATIVE = 'alternative'


@dataclass
class HighlightedPosition(ValuePosition):
    indicator_level: IndicatorLevel = None

    def __hash__(self):
        """return same hash if complete position matches (x+y+value), this also applies to
        subclasses, i.e. hash will not consider indicator level"""
        return hash((self.x, self.y, self.value,))


@dataclass
class PreviewArrow:
    pos_from: ValuePosition
    pos_to: ValuePosition
    indicator_level: Optional[IndicatorLevel] = None


class Preview(Protocol):
    def execute(self) -> None:
        """execute the invalidation of candidates"""

    def get_indicator_arrows(self) -> Sequence[PreviewArrow]:
        """return the arrow board positions indicating loops, chains, etc."""

    def get_preview_line_nodes(self) -> Sequence[ValuePosition]:
        """get the nodes of a preview line, e.g. from chain start to chain end"""

    def get_invalidated_candidates(self) -> Sequence[ValuePosition]:
        """get the candidate positions to be invalidated"""

    def get_indicator_candidates(self) -> Sequence[HighlightedPosition]:
        """get candidate positions to be highlighted"""


class CommonPreview(Preview):
    """simple preview object util by multiple algorithms with no algorithm-specific logic"""

    def __init__(self,
                 invalidated_cells: Sequence[Tuple[Cell, int]],  # Cell, Candidate
                 indicator_candidates: Sequence[HighlightedPosition] = tuple(),
                 indicator_arrows: Sequence[PreviewArrow] = tuple()):
        self.invalidated_cells = invalidated_cells
        self.indicator_candidates = indicator_candidates
        self.indicator_arrows = indicator_arrows

    def get_indicator_candidates(self) -> Sequence[HighlightedPosition]:
        """return the board positions of base row candidates"""
        return self.indicator_candidates

    def get_indicator_arrows(self) -> Sequence[PreviewArrow]:
        """return the arrow board positions indicating loops, chains, etc."""
        return self.indicator_arrows

    def get_invalidated_candidates(self) -> Sequence[ValuePosition]:
        """return the board positions where the candidate is invalidated"""
        inv = []
        for cell, candidate in self.invalidated_cells:
            inv.append(ValuePosition(x=cell.x, y=cell.y, value=candidate))
        return tuple(inv)

    def execute(self):
        for cell, candidate in self.invalidated_cells:
            cell.flag_candidates_invalid([candidate])