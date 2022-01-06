from typing import Sequence

from sudoku_solver.shared.puzzle import PrefilledValue, SudokuPuzzle


def _parse_sudoku(sudoku_rows: Sequence[str]) -> SudokuPuzzle:  # y, x -> candidate
    # sudoku_ = {}
    prefilled_values = []
    assert (len(sudoku_rows) == 9)
    for i, row in enumerate(sudoku_rows, 1):
        for x, c in enumerate(row, 1):
            if c in '123456789':
                y = i
                prefilled_value = PrefilledValue(x=x, y=y, value=int(c))
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