from sudoku_solver.board.board import Board
from sudoku_solver.shared.puzzle import SudokuPuzzle
# from sudoku_solver.solver.algorithms import get_algo_invalidate_solved_values, get_algo_find_single_candidates, \
#     get_algo_invalidate_with_n_fish, \
#     get_algorithm
# from sudoku_solver.solver.almost_locked_sets import find_singly_or_doubly_linked_als
# from sudoku_solver.solver.chains import find_x_chain, find_xy_chain
# from sudoku_solver.solver.empty_rectangle import find_empty_rectangle
# from sudoku_solver.solver.hidden_subset import find_hidden_subset
# from sudoku_solver.solver.locked_candidate import find_locked_candidate
# from sudoku_solver.solver.naked_subset import find_naked_subset
# from sudoku_solver.solver.nice_loop import find_nice_loop
# from sudoku_solver.solver.remote_pair import find_remote_pair
# from sudoku_solver.solver.skyscraper import find_skyscraper
# from sudoku_solver.solver.sue_de_coq import find_sue_de_coq
# from sudoku_solver.solver.two_string_kite import find_two_string_kite
# from sudoku_solver.solver.uniqueness import find_uniqueness_violations
# from sudoku_solver.solver.w_wing import find_w_wing
# from sudoku_solver.solver.xy_z_wing import find_xyz_wing, find_xy_wing
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
    board.subscribe_preview(observer_preview=sudoku_ui.observe_preview)

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