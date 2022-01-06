import tkinter

from sudoku_solver.shared.puzzle import SudokuPuzzle
from sudoku_solver.ui.ui_constants import WIDTH, BUTTONS_WIDTH, HEIGHT
from sudoku_solver.ui.ui import SudokuUI


def run_ui_loop(sudoku_ui: SudokuUI):
    sudoku_ui.tk.geometry(f'{WIDTH + BUTTONS_WIDTH}x{HEIGHT}')
    sudoku_ui.tk.mainloop()


def init_ui(prefilled_values: SudokuPuzzle) -> SudokuUI:
    tk = tkinter.Tk()
    sudoku_ui = SudokuUI(tk)
    sudoku_ui.prefill_values(prefilled_values)
    return sudoku_ui