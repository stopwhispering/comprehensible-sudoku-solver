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

        self.x = x
        self.y = y
        self.z = self._get_block(x, y)
        self.possible_values: List[int] = list(range(1, 10)) if not prefilled_value else [prefilled_value]

        self.row: Optional[Row] = None
        self.column: Optional[Column] = None
        self.block: Optional[Block] = None

    def __repr__(self):
        candidates = [str(cand) for cand in self.possible_values]
        values = f'-> {str(self.value)} <- ' if self.is_solved() else ''.join(candidates)
        return f'Cell {self.x}/{self.y}/{self.z}: {values}'

    @property
    def value(self):
        return self.possible_values[0] if self.is_solved() else None

    def is_solved(self):
        assert self.possible_values
        return len(self.possible_values) == 1

    def is_value_candidate(self, value: int):
        return value in self.possible_values

    def set_solved_value_to(self, value: int):
        """remove all candidates but value from list of possible candidates;
        must be unsolved before"""
        assert not self.is_solved()
        assert value in self.possible_values
        self.flag_invalid_all_but([value])
        self.notify_finishing_value(x=self.x, y=self.y, value=value)

    def flag_candidates_invalid(self, values: Iterable[int]):
        for value in values:
            if value in self.possible_values:
                self.possible_values.remove(value)
                self.notify_invalidating_candidate(x=self.x, y=self.y, invalidated_value=value)

        if self.is_solved():
            self.notify_finishing_value(x=self.x, y=self.y, value=self.value)

    def flag_invalid_all_but(self, values: List[int]):
        for value in values:
            assert self.is_value_candidate(value)
        invalidate = [c for c in self.possible_values if c not in values]
        self.flag_candidates_invalid(invalidate)

    def get_linked_cells(self, candidate: int, link_type: LinkType, n_candidates: int = None) -> Set[Cell]:
        """optional filter on only linked cells with exactly n total candidates"""
        assert candidate in self.possible_values
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

    def seen_by(self, candidate: int) -> Set[Cell]:
        """return all other cells seeing this cell considering supplied candidate; consider all houses (row, column,
        block"""
        seen_by_raw = (self.column.get_cells_having_candidate(candidate=candidate) +
                       self.row.get_cells_having_candidate(candidate=candidate) +
                       self.block.get_cells_having_candidate(candidate=candidate))
        seen_by = [c for c in seen_by_raw if c is not self]
        return set(seen_by)

    def seen_by_any_of_candidates(self, candidates: Sequence[int]) -> Set[Cell]:
        """return all other cells seeing this cell which have any (i.e. one or more) of the supplied candidates;
        consider all houses (row, column,block"""
        seen_by_raw = (self.column.get_cells_having_any_of_candidates(candidates=candidates) +
                       self.row.get_cells_having_any_of_candidates(candidates=candidates) +
                       self.block.get_cells_having_any_of_candidates(candidates=candidates))
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
        if x >= 6 and y >= 6:
            block = 8
        elif x >= 6 and y >= 3:
            block = 5
        elif x >= 6 and y < 3:
            block = 2
        elif x >= 3 and y >= 6:
            block = 7
        elif x >= 3 and y >= 3:
            block = 4
        elif x >= 3 and y < 3:  # noqa
            block = 1
        elif x < 3 and y >= 6:
            block = 6
        elif x < 3 and y >= 3:  # noqa
            block = 3
        elif x < 3 and y < 3:
            block = 0
        else:
            raise ValueError

        return block
