import itertools
from typing import Dict, Tuple, List, Set
import pandas as pd

from sudoku_solver.board.houses import Row, Column, Block, House
from sudoku_solver.board.cell import Cell
from sudoku_solver.board.observable import SudokuObservable
from sudoku_solver.board.board_constants import HORIZONTAL_INDEXES, VERTICAL_INDEXES


class Board(SudokuObservable):
    def __init__(self, prefilled_values: Dict[Tuple, int]):
        super().__init__()
        # make sure they're sorted
        self.rows: Dict[int, Row] = {y: Row(y=y) for y in range(9)}
        self.columns: Dict[int, Column] = {x: Column(x=x) for x in range(9)}
        self.blocks: Dict[int, Block] = {z: Block() for z in range(9)}

        self._initialize_cells(prefilled_values=prefilled_values)

    def _initialize_cells(self, prefilled_values: Dict[Tuple, int]):
        # loop at all cell positions and instantiate all cells
        cells = []
        for position in itertools.product(HORIZONTAL_INDEXES, VERTICAL_INDEXES):
            cell = Cell(x=position[0],
                        y=position[1],
                        prefilled_value=prefilled_values.get(position))
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

    def substribe_observer_to_cells(self,
                                    observer_finishing_value: callable,
                                    observer_invalidating_candidate: callable):
        """subscribe an observer (GUI) to all cells. They will emit changes to values
        and invalidated candidates"""
        for cell in self._get_all_cells():
            cell.observe_finishing_value(observer=observer_finishing_value)
            cell.observe_invalidating_candidate(observer=observer_invalidating_candidate)

    def as_df(self, mode='values') -> pd.DataFrame:
        series = {}
        for x, column in self.columns.items():
            series[x] = column.as_series(mode=mode)
        return pd.DataFrame(data=series).sort_index(ascending=False)

    def _get_all_cells(self, only_unsolved: bool = False) -> List[Cell]:
        """get list of all cells"""
        cells = [c for block in self.blocks.values() for c in block.get_cells()]
        if not only_unsolved:
            return cells
        else:
            unsolved_cells = [c for c in cells if not c.is_solved()]
            return unsolved_cells

    def get_cells_by_candidate(self, candidate: int, n_candidates: int = None):
        """return all cells that have certain candidate;
        optionally filter on cells that have exactly n candidates left"""
        all_cells = self._get_all_cells()
        cells = [c for c in all_cells if c.is_value_candidate(candidate)]
        if not n_candidates:
            return cells
        else:
            return [c for c in cells if len(c.possible_values) == n_candidates]

    def get_cells_by_number_of_candidates(self, n_candidates: int):
        """return all cells that have exactly n candidates left"""
        assert 1 < n_candidates <= 9
        unsolved_cells = self._get_all_cells(only_unsolved=True)
        cells = [c for c in unsolved_cells if len(c.possible_values) == n_candidates]
        return cells

    def get_count_remaining_candidates(self):
        all_cells = self._get_all_cells()
        remaining = [len(c.possible_values) for c in all_cells if not c.is_solved()]
        return sum(remaining)

    def get_count_solved(self):
        all_cells = self._get_all_cells()
        return len([c for c in all_cells if c.is_solved()])

    def get_count_unsolved(self):
        all_cells = self._get_all_cells()
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

    def get_all_houses(self) -> List[House]:
        """returns all rows, cols, and blocks"""
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
        cells_seeing_a = cell_a.seen_by(candidate=candidate)
        cells_seeing_b = cell_b.seen_by(candidate=candidate)
        cells_seeing_both = cells_seeing_a.intersection(cells_seeing_b)
        return cells_seeing_both
