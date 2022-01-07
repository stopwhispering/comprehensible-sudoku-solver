from dataclasses import dataclass
from typing import List, Optional, Sequence


@dataclass
class ValuePosition:
    x: int
    y: int
    value: int

    def __hash__(self):
        """return same hash if complete position matches (x+y+value)"""
        return hash((self.x, self.y, self.value,))

    def __eq__(self, other):
        return hash(self) == hash(other)


class SudokuPuzzle:
    def __init__(self, prefilled_values: List[ValuePosition]):
        self.prefilled_values = prefilled_values

    def get(self, x: int, y: int) -> Optional[int]:
        values = [p for p in self.prefilled_values if p.x == x and p.y == y]
        if values:
            return values[0].value


def _parse_sudoku(sudoku_rows: Sequence[str]) -> SudokuPuzzle:  # y, x -> candidate
    # sudoku_ = {}
    prefilled_values = []
    assert (len(sudoku_rows) == 9)
    for i, row in enumerate(sudoku_rows, 1):
        for x, c in enumerate(row, 1):
            if c in '123456789':
                y = i
                prefilled_value = ValuePosition(x=x, y=y, value=int(c))
                prefilled_values.append(prefilled_value)

    return SudokuPuzzle(prefilled_values=prefilled_values)


def read_sudoku_file(path: str) -> SudokuPuzzle:
    sudoku_rows = []
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip().startswith('#'):
                continue
            if [r for r in line.rstrip() if not r.isdigit() and not r == ' ']:
                raise TypeError
            sudoku_rows.append(line.rstrip())
    sudoku = _parse_sudoku(sudoku_rows)
    return sudoku