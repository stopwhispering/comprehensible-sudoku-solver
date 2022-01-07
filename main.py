import os.path

from sudoku_solver.shared.constants import SUDOKU_DIR, DEFAULT_SUDOKU
from sudoku_solver.shared.puzzle import read_sudoku_file
from sudoku_solver.init import start_sudoku

if __name__ == '__main__':
    sudoku = read_sudoku_file(path=os.path.join(SUDOKU_DIR, DEFAULT_SUDOKU))
    start_sudoku(sudoku=sudoku)



