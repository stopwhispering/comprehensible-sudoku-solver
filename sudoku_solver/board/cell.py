from __future__ import annotations
from typing import TYPE_CHECKING, Sequence

from typing import Optional, List, Iterable, Set

if TYPE_CHECKING:
    from sudoku_solver.board.houses import Row, Column, Block
from sudoku_solver.board.board_constants import LinkType
from sudoku_solver.board.observable import SudokuObservable


class Cell(SudokuObservable):
    def __init__(self, x: int, y: int, prefilled_value: int = None):
        super().__init__()

        self.x: int = x
        self.y: int = y
        self.z = self._get_block(x, y)
        self.candidates: List[int] = list(range(1, 10)) if not prefilled_value else [prefilled_value]

        self.row: Optional[Row] = None
        self.column: Optional[Column] = None
        self.block: Optional[Block] = None

    def __repr__(self):
        candidates = [str(cand) for cand in self.candidates]
        values = f'-> {str(self.value)} <- ' if self.is_solved() else ''.join(candidates)
        return f'r{self.y}c{self.x}({values})'

    @property
    def value(self) -> Optional[int]:
        return self.candidates[0] if self.is_solved() else None

    @property
    def count_candidates(self) -> int:
        return len(self.candidates)

    def is_solved(self) -> bool:
        assert self.candidates
        return len(self.candidates) == 1

    def has_candidate(self, candidate: int) -> bool:
        return candidate in self.candidates

    def has_exactly_candidates(self, candidates: Sequence[int]) -> bool:
        return set(candidates) == set(self.candidates)

    def set_solved_value_to(self, value: int) -> None:
        """remove all candidates but candidate from list of possible candidates;
        must be unsolved before"""
        assert not self.is_solved()
        assert self.has_candidate(value)
        invalidate = [c for c in self.candidates if c != value]
        self.flag_candidates_invalid(invalidate)
        self.notify_finishing_value(y=self.y, x=self.x, value=value)

    def flag_candidates_invalid(self, candidates: Iterable[int]):
        for candidate in candidates:
            if candidate in self.candidates:
                self.candidates.remove(candidate)
                self.notify_invalidating_candidate(y=self.y, x=self.x, invalidated_value=candidate)

        if self.is_solved():
            self.notify_finishing_value(y=self.y, x=self.x, value=self.value)

    def get_linked_cells(self, candidate: int, link_type: LinkType, n_candidates: int = None) -> Set[Cell]:
        """optional filter on only linked cells with exactly n total candidates"""
        assert candidate in self.candidates
        # find another cell that is strongly linked considering our candidate
        row_cells = [c for c in self.row.get_cells_having_candidate(candidate, n_candidates=n_candidates)
                     if c is not self]
        col_cells = [c for c in self.column.get_cells_having_candidate(candidate, n_candidates=n_candidates)
                     if c is not self]
        block_cells = [c for c in self.block.get_cells_having_candidate(candidate, n_candidates=n_candidates)
                       if c is not self]

        linked = []
        if link_type == LinkType.STRONG or link_type == LinkType.ANY:
            strongly_linked_nested = [cells for cells in (row_cells, col_cells, block_cells) if len(cells) == 1]
            linked.extend([cell for cells in strongly_linked_nested for cell in cells])

        if link_type == LinkType.WEAK or link_type == LinkType.ANY:
            weakly_linked_nested = [cells for cells in (row_cells, col_cells, block_cells) if len(cells) >= 1]
            linked.extend([cell for cells in weakly_linked_nested for cell in cells])

        linked_distinct = set(linked)
        return linked_distinct

    def seen_by(self, candidate: int, n_candidates: int = None) -> Set[Cell]:
        """return all other cells seeing this cell considering supplied candidate; consider all houses (row, column,
        block; optionally limit to cells having n candidates"""
        seen_by_raw = (self.column.get_cells_having_candidate(candidate=candidate, n_candidates=n_candidates) +
                       self.row.get_cells_having_candidate(candidate=candidate, n_candidates=n_candidates) +
                       self.block.get_cells_having_candidate(candidate=candidate, n_candidates=n_candidates))
        seen_by = [c for c in seen_by_raw if c is not self]
        return set(seen_by)

    def seen_by_any_of_candidates(self, candidates: Sequence[int], except_cells: Sequence[Cell] = tuple()) -> Set[Cell]:
        """return all other cells seeing this cell which have any (i.e. one or more) of the supplied candidates;
        consider all houses (row, column,block)"""
        seen_by_raw = (self.column.get_cells_having_any_of_candidates(candidates, except_cells=except_cells) +
                       self.row.get_cells_having_any_of_candidates(candidates, except_cells=except_cells) +
                       self.block.get_cells_having_any_of_candidates(candidates, except_cells=except_cells))
        seen_by = [c for c in seen_by_raw if c is not self]
        return set(seen_by)

    def seen_by_with_all_candidates(self, candidates: Sequence[int]) -> Set[Cell]:
        """return all other cells seeing this cell which have all the supplied candidates;
        consider all houses (row, column,block)"""
        seen_by_raw = (self.column.get_cells_having_each_of_candidates(candidates=candidates) +
                       self.row.get_cells_having_each_of_candidates(candidates=candidates) +
                       self.block.get_cells_having_each_of_candidates(candidates=candidates))
        seen_by = [c for c in seen_by_raw if c is not self]
        return set(seen_by)

    def seen_by_with_exact_candidates(self, candidates: Sequence[int]) -> Set[Cell]:
        """return all other cells seeing this cell which have exactly the supplied candidates;
        consider all houses (row, column,block)"""
        seen_by_raw = (self.column.get_cells_having_exact_candidates(candidates=candidates) +
                       self.row.get_cells_having_exact_candidates(candidates=candidates) +
                       self.block.get_cells_having_exact_candidates(candidates=candidates))
        seen_by = [c for c in seen_by_raw if c is not self]
        return set(seen_by)

    def is_seen_by_cell(self, other_cell: Cell):
        """returns True if in same house; doesn't consider candidate"""
        if self.row is other_cell.row or self.column is other_cell.column or self.block is other_cell.block:
            return True
        else:
            return False

    def set_row(self, row: Row):
        self.row = row

    def set_column(self, column: Column):
        self.column = column

    def set_block(self, block: Block):
        self.block = block

    @staticmethod
    def _get_block(x: int, y: int) -> int:
        if 7 <= x <= 9 and 7 <= y <= 9:
            block = 9
        elif 7 <= x <= 9 and 4 <= y <= 6:  # noqa
            block = 6
        elif 7 <= x <= 9 and 1 <= y <= 3:
            block = 3
        elif 4 <= x <= 6 and 7 <= y <= 9:  # noqa
            block = 8
        elif 4 <= x <= 6 and 4 <= y <= 6:
            block = 5
        elif 4 <= x <= 6 and 1 <= y <= 3:  # noqa
            block = 2
        elif 1 <= x <= 3 and 7 <= y <= 9:
            block = 7
        elif 1 <= x <= 3 and 4 <= y <= 6:  # noqa
            block = 4
        elif 1 <= x <= 3 and 1 <= y <= 3:
            block = 1
        else:
            raise ValueError

        return block
