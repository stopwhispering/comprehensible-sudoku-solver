from enum import Enum
from typing import Dict, List, Union, Sequence, Set, Tuple, Iterable
import pandas as pd

from sudoku_solver.board.cell import Cell


class HouseType(Enum):
    ROW = 'row'
    COL = 'col'
    BLOCK = 'block'


class House:
    """superclass for Row, Column, and Block"""

    def __init__(self):
        # make sure cells are sorted
        self.cells: Dict[int, Cell] = {n: None for n in range(1, 10)}

    def __contains__(self, item):
        if isinstance(item, Cell):
            return item in self.get_cells()
        else:
            raise ValueError('Unknown Object')

    @property
    def finished_values(self) -> List[int]:
        return self.get_finished_values()

    @property
    def candidates(self) -> Set[int]:
        unsolved_cells = self.get_cells(only_unsolved=True)
        candidates = [c for cell in unsolved_cells for c in cell.candidates]
        return set(candidates)

    def as_series(self, mode=Union['candidates', 'candidates']) -> pd.Series:
        """
        don't use for blocks
        mode == 'candidates' or 'candidates'
        """
        if mode == 'candidates':
            values = [cell.value for cell in self.cells.values()]
            return pd.Series(values, dtype="Int64")

        elif mode == 'candidates':
            candidates = [cell.candidates for cell in self.cells.values()]
            candidates_str = [[str(c) for c in li] for li in candidates]
            candidates_concat = [''.join(c) for c in candidates_str]
            return pd.Series(candidates_concat)  # object

    def validate_finished(self) -> bool:
        """check if all candidates are set and dimension is consistent"""
        values = [cell.value for cell in self.cells.values() if cell.value]
        distinct_values = set(values)
        return len(distinct_values) == 9

    def get_finished_values(self) -> List[int]:
        solved_cells = self.get_cells(only_solved=True)
        return [c.value for c in solved_cells]

    def get_unfinished_values(self) -> List[int]:
        all_values = list(range(1, 10))
        finished_values = self.get_finished_values()
        return [v for v in all_values if v not in finished_values]

    def invalidate_solved_values(self):
        """invalidate solved candidates from this row/column/block as invalid in all other cells"""
        values = self.get_finished_values()
        unsolved_cells = self.get_cells(only_unsolved=True)
        for value in values:
            for cell in (c for c in unsolved_cells if c.has_candidate(value)):
                cell.flag_candidates_invalid(candidates=[value])
        self.validate_consistency()

    def validate_consistency(self):
        """print a warning if there's an inconcistency in this row/col/package, e.g. two times same number"""
        values = [cell.value for cell in self.cells.values() if cell.value]
        duplicates = set([x for x in values if values.count(x) > 1])
        if duplicates:
            raise ValueError(f'Found Inconsistency - Duplicate(s) in {self}: {duplicates}')

        candidates = [cell.candidates for cell in self.cells.values() if not cell.is_solved()]
        flat = [c for cell_candidates in candidates for c in cell_candidates] + values
        candidates_distinct = set(flat)
        missing = set(range(1, 10)).difference(candidates_distinct)
        if missing:
            raise ValueError(f'Found Inconsistency - Candidate(s) missing in {self}: {missing}')

    def get_cells(self, only_unsolved=False, only_solved=False) -> List[Cell]:
        if only_solved:
            return [c for c in self.cells.values() if c.is_solved()]
        elif only_unsolved:
            return [c for c in self.cells.values() if not c.is_solved()]
        else:
            return list(self.cells.values())

    def get_count_of_cells_having_candidate(self, candidate: int):
        all_cells = self.get_cells(only_unsolved=True)
        return len([c for c in all_cells if c.has_candidate(candidate)])

    def get_cells_having_candidate(self, candidate: int,
                                   n_candidates: int = None,
                                   except_cells: Sequence[Cell] = None) -> List[Cell]:
        """returns all cells of this house that have supplied candidate;
        optionally filter on only cells with exactly n total candidates;
        optionally filter on cells that are not in supplied exeption list
        """
        all_cells = self.get_cells(only_unsolved=True)
        if n_candidates:
            cells = [c for c in all_cells if candidate in c.candidates and len(c.candidates) == n_candidates]
        else:
            cells = [c for c in all_cells if candidate in c.candidates]
        if except_cells:
            cells = [c for c in cells if c not in except_cells]
        return cells

    def get_cells_having_any_of_candidates(self,
                                           candidates: Sequence[int],
                                           except_cells: Sequence[Cell] = tuple(),
                                           n_candidates: int = None,
                                           ) -> List[Cell]:
        all_cells = self.get_cells(only_unsolved=True)
        cells = [c for c in all_cells if not set(candidates).isdisjoint(c.candidates) and c not in except_cells]
        if n_candidates:
            cells = [c for c in cells if len(c.candidates) == n_candidates]
        return cells

    def get_cells_having_each_of_candidates(self, candidates: Sequence[int]):
        """return cells having at least the supplied candidates, i.e. possibly others as well"""
        all_cells = self.get_cells(only_unsolved=True)
        cells = [c for c in all_cells if set(c.candidates).issuperset(candidates)]
        return cells

    def get_cells_having_only_candidates(self,
                                         candidates: Iterable[int],
                                         except_cells: Sequence[Cell] = None,
                                         n_candidates: int = None):
        """return cells that have only supplied candidates, i.e. no other candidates"""
        all_cells = self.get_cells(only_unsolved=True)
        cells = [c for c in all_cells if set(candidates).issuperset(c.candidates)]
        if n_candidates:
            cells = [c for c in cells if len(c.candidates) == n_candidates]
        if except_cells:
            cells = [c for c in cells if c not in except_cells]
        return cells

    def get_cells_having_exact_candidates(self, candidates: Sequence[int]):
        """return cells that have exactly the supplied candidates, i.e. no less and no more"""
        all_cells = self.get_cells(only_unsolved=True)
        cells = [c for c in all_cells if set(candidates) == set(c.candidates)]
        return cells

    def solve_single_candidates(self):
        """find candidate that is existent in only one cell"""
        cells = self.get_cells(only_unsolved=True)
        values = [v for v in range(1, 10) if v not in self.get_finished_values()]
        for value in values:
            cells_having_that_candidate = [c for c in cells if value in c.candidates]
            if len(cells_having_that_candidate) == 1:
                cells_having_that_candidate[0].set_solved_value_to(value)
            # return
        self.validate_consistency()

    def get_unsolved_intersection_with_other_house(self, other_house) -> Tuple[Cell]:
        assert self is not other_house
        cells_self = self.get_cells(only_unsolved=True)
        cells = tuple((c for c in cells_self if c in other_house))
        return cells

    @staticmethod
    def cells_in_same_row(cells: Sequence[Cell]):
        """returns true if all supplied cells are in the same row"""
        rows = [c.row for c in cells]
        return len(set(rows)) == 1

    @staticmethod
    def cells_in_same_col(cells: Sequence[Cell]):
        """returns true if all supplied cells are in the same column"""
        cols = [c.column for c in cells]
        return len(set(cols)) == 1

    @staticmethod
    def cells_in_same_block(cells: Sequence[Cell]):
        """returns true if all supplied cells are in the same block"""
        blocks = [c.block for c in cells]
        return len(set(blocks)) == 1


class Row(House):
    def __init__(self, y: int):
        super().__init__()
        self.y = y

    def __repr__(self):
        return f'r{self.y}'

    def initialize_cell(self, cell: Cell):
        assert not self.cells.get(cell.x)
        self.cells[cell.x] = cell
        cell.set_row(row=self)


class Column(House):
    def __init__(self, x: int):
        super().__init__()
        self.x = x

    def __repr__(self):
        return f'c{self.x}'

    def initialize_cell(self, cell: Cell):
        assert not self.cells.get(cell.y)
        self.cells[cell.y] = cell
        cell.set_column(column=self)


class Block(House):
    def __init__(self, z: int):
        super().__init__()
        # override as we have a composite key for our cells
        self.cells: Dict[(int, int), Cell] = {}
        self.z = z

    def __repr__(self):
        return f'block {self.z}'

    def initialize_cell(self, cell: Cell):
        assert (cell.x, cell.y) not in self.cells
        self.cells[(cell.x, cell.y)] = cell
        cell.set_block(block=self)

    def get_crossing_houses(self, house_type: HouseType = None) -> Set[House]:
        if house_type:
            if house_type is HouseType.ROW:
                rows = set([c.row for c in self.get_cells()])
            elif house_type is HouseType.COL:
                cols = set([c.column for c in self.get_cells()])
            else:
                raise TypeError('No valid House Type')
        return set([c.row for c in self.get_cells()] + [c.column for c in self.get_cells()])

