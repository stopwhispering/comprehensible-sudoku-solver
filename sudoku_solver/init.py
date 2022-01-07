from sudoku_solver.board.board import Board
from sudoku_solver.shared.puzzle import SudokuPuzzle
from sudoku_solver.solver.algorithms import get_algorithms
from sudoku_solver.ui.loop import run_ui_loop, init_ui


def start_sudoku(sudoku: SudokuPuzzle, running_ui=None):
    if running_ui:
        running_ui.tk.destroy()

    board = Board(prefilled_values=sudoku)
    # have board and ui in sync via observer pattern
    sudoku_ui = init_ui(prefilled_values=sudoku)
    board.substribe_observer_to_cells(observer_finishing_value=sudoku_ui.observe_finishing_value,
                                      observer_invalidating_candidate=sudoku_ui.observe_invalidating_candidate)
    board.subscribe_to_previews(observer_preview=sudoku_ui.observe_preview)

    # we need to inject the board to enable the decoration of algorithm functions
    from sudoku_solver.solver.decorators import board_cache
    board_cache['current'] = board
    sudoku_ui.set_algorithms(algorithms=get_algorithms(board=board))

    # stats = Stats(board)
    # print(f'Original Board')
    # stats.shout_current_status()
    # board.validate_finished_board()

    # board.as_df(mode='candidates').to_clipboard()
    run_ui_loop(sudoku_ui=sudoku_ui)