import itertools
from typing import Dict, List, Set, Sequence
import pandas as pd

from sudoku_solver.board.houses import Row, Column, Block, House, HouseType
from sudoku_solver.board.cell import Cell
from sudoku_solver.board.observable import SudokuObservable
from sudoku_solver.board.board_constants import HORIZONTAL_INDEXES, VERTICAL_INDEXES
from sudoku_solver.shared.puzzle import SudokuPuzzle


class Board(SudokuObservable):
    def __init__(self, prefilled_values: SudokuPuzzle):
        super().__init__()
        # make sure they're sorted
        self.rows: Dict[int, Row] = {y: Row(y=y) for y in range(1, 10)}
        self.columns: Dict[int, Column] = {x: Column(x=x) for x in range(1, 10)}
        self.blocks: Dict[int, Block] = {z: Block(z=z) for z in range(1, 10)}

        self._initialize_cells(prefilled_values=prefilled_values)

    def _initialize_cells(self, prefilled_values: SudokuPuzzle):
        # loop at all cell positions and instantiate all cells
        cells = []
        for position in itertools.product(HORIZONTAL_INDEXES, VERTICAL_INDEXES):
            cell = Cell(x=position[1],
                        y=position[0],
                        prefilled_value=prefilled_values.get(x=position[1], y=position[0]))
            cells.append(cell)

        # fill cells into their respective row, column, and block
        # also attach the container to the cell for cross-navigation
        for cell in cells:
            self.rows[cell.y].initialize_cell(cell)
            self.columns[cell.x].initialize_cell(cell)
            self.blocks[cell.z].initialize_cell(cell)

        assert len(self.rows) == 9
        assert len(self.columns) == 9
        assert len(self.blocks) == 9

    def get_cell(self, y: int, x: int) -> Cell:
        all_cells = self.get_cells()
        cells = [c for c in all_cells if c.x == x and c.y == y]
        assert len(cells) == 1
        return cells[0]

    def substribe_observer_to_cells(self,
                                    observer_finishing_value: callable,
                                    observer_invalidating_candidate: callable):
        """subscribe an observer (GUI) to all cells. They will emit changes to candidates
        and invalidated candidates"""
        for cell in self.get_cells():
            cell.subscribe_to_finished_values(observer=observer_finishing_value)
            cell.subscribe_to_invalidated_candidates(observer=observer_invalidating_candidate)

    def as_df(self, mode='candidates') -> pd.DataFrame:
        series = {}
        for x, column in self.columns.items():
            series[x] = column.as_series(mode=mode)
        return pd.DataFrame(data=series).sort_index(ascending=False)

    def get_cells(self, only_unsolved: bool = False) -> List[Cell]:
        """get list of all cells"""
        cells = [c for block in self.blocks.values() for c in block.get_cells()]
        if not only_unsolved:
            return cells
        else:
            unsolved_cells = [c for c in cells if not c.is_solved()]
            return unsolved_cells

    def get_cells_by_candidate(self, candidate: int,
                               n_candidates: int = None,
                               except_cells: Sequence[Cell] = None):
        """return all cells that have certain candidate;
        optionally filter on cells that have exactly n candidates left
        optionally exclude supplied cells"""
        all_cells = self.get_cells(only_unsolved=True)
        cells = [c for c in all_cells if c.has_candidate(candidate)]
        if except_cells:
            cells = [c for c in cells if c not in except_cells]
        if not n_candidates:
            return cells
        else:
            return [c for c in cells if len(c.candidates) == n_candidates]

    def get_cells_by_exact_candidates(self, candidates: Sequence[int]):
        """return all cells that have <<exactly>> supplied candidates"""
        all_cells = self.get_cells(only_unsolved=True)
        cells = [c for c in all_cells if c.has_exactly_candidates(candidates=candidates)]
        return cells

    def get_cells_having_candidates(self, candidates: Sequence[int], n_candidates: int = None):
        """return all cells that have at least supplied candidates, i.e. possibly others, too
        optionally filter on cells that have exactly n candidates left"""
        all_cells = self.get_cells(only_unsolved=True)
        cells = [c for c in all_cells if set(c.candidates).issuperset(candidates)]
        if n_candidates:
            cells = [c for c in cells if len(c.candidates) == n_candidates]
        return cells

    def get_cells_by_number_of_candidates(self, n_candidates: int) -> List[Cell]:
        """return all cells that have exactly n candidates left"""
        assert 1 < n_candidates <= 9
        unsolved_cells = self.get_cells(only_unsolved=True)
        cells = [c for c in unsolved_cells if len(c.candidates) == n_candidates]
        return cells

    def get_count_remaining_candidates(self):
        all_cells = self.get_cells()
        remaining = [len(c.candidates) for c in all_cells if not c.is_solved()]
        return sum(remaining)

    def get_count_solved(self):
        all_cells = self.get_cells()
        return len([c for c in all_cells if c.is_solved()])

    def get_count_unsolved(self):
        all_cells = self.get_cells()
        return len([c for c in all_cells if not c.is_solved()])

    def validate_finished_board(self):
        validated = []
        for row in self.rows.values():
            validated.append(row.validate_finished())
        for column in self.columns.values():
            validated.append(column.validate_finished())
        for block in self.blocks.values():
            validated.append(block.validate_finished())
        if all(validated):
            print('All finished')
        else:
            print('Not finished')

    def validate_consistency_in_all_houses(self):
        units = self.get_all_houses()
        for unit in units:
            unit.validate_consistency()

    def get_all_houses(self, house_type: HouseType = None) -> List[House]:
        """returns all rows, cols, and blocks"""
        if house_type is HouseType.ROW:
            return list(self.rows.values())
        elif house_type is HouseType.COL:
            return list(self.columns.values())
        elif house_type is HouseType.BLOCK:
            return list(self.blocks.values())
        return list(self.rows.values()) + list(self.columns.values()) + list(self.blocks.values())  # noqa

    @staticmethod
    def get_cells_same_band(cells: List[Cell], mode: str):
        """mode either 'horizontal' or 'vertical'"""
        if mode == 'vertical':
            bands = [(c.column.x // 3) for c in cells]
        elif mode == 'horizontal':
            bands = [(c.row.y // 3) for c in cells]
        else:
            raise ValueError
        return len(set(bands)) == 1

    @staticmethod
    def get_cells_seeing_both_supplied_cells(candidate: int, cell_a: Cell, cell_b: Cell) -> Set[Cell]:
        # todo replace by generic version below
        cells_seeing_a = cell_a.seen_by(candidate=candidate)
        cells_seeing_b = cell_b.seen_by(candidate=candidate)
        cells_seeing_both = cells_seeing_a.intersection(cells_seeing_b)
        return cells_seeing_both

    @staticmethod
    def get_cells_seeing_all_supplied_cells(candidate: int, cells: Sequence[Cell]) -> Set[Cell]:
        cells_seeing = [cell.seen_by(candidate=candidate) for cell in cells]
        cells_seeing_each = set.intersection(*cells_seeing)
        return set([cell for cell in cells_seeing_each if cell not in cells])

    @staticmethod
    def are_cell_sets_seeing_each_other(candidate: int, cells_a: Sequence[Cell], cells_b: Sequence[Cell]) -> bool:
        """returns true if each cell of cells_a sees each cell of cells_b (and the other way around)"""
        for cell in cells_a:
            cells_seen = cell.seen_by(candidate=candidate)
            if not cells_seen.issuperset(cells_b):
                return False
        return True

    @staticmethod
    def get_houses_shared_by_cells(cells: Sequence[Cell]) -> List[House]:
        rows = [c.row for c in cells]
        cols = [c.column for c in cells]
        blocks = [c.block for c in cells]
        shared = []
        if len(set(rows)) == 1:
            shared.append(rows[0])
        if len(set(cols)) == 1:
            shared.append(cols[0])
        if len(set(blocks)) == 1:
            shared.append(blocks[0])
        return shared

    @staticmethod
    def are_cells_in_same_house(cells: Sequence[Cell]):
        """returns true if all cells in sequence share a single house (either all in same row, all in same col,
        or all in same block"""
        rows = set([cell.row for cell in cells])
        cols = set([cell.column for cell in cells])
        blocks = set([cell.block for cell in cells])
        return len(rows) == 1 or len(cols) == 1 or len(blocks) == 1

    @staticmethod
    def get_common_houses(cells: Sequence[Cell]) -> List[House]:
        """check if supplied cells share one (or many) single house; return them"""
        rows = set([cell.row for cell in cells])
        cols = set([cell.column for cell in cells])
        blocks = set([cell.block for cell in cells])
        shared_houses = []
        if len(rows) == 1:
            shared_houses.append(rows.pop())
        if len(cols) == 1:
            shared_houses.append(cols.pop())
        if len(blocks) == 1:
            shared_houses.append(blocks.pop())
        return shared_houses

    @staticmethod
    def get_distinct_candidates(cells: Sequence[Cell]) -> Set[int]:
        return set((c for cell in cells for c in cell.candidates))