from sudoku_solver.solver.algorithms import get_algo_remote_pair, get_algo_two_string_kite, get_algo_xyz_wing, \
    get_algo_locked_candidate, get_algo_singly_or_doubly_linked_als, get_algo_w_wing, get_algo_discontinuous_nice_loop, \
    get_algo_uniqueness_violations, get_algo_sue_de_coq, get_algo_empty_rectangle
from sudoku_solver.solver.algorithms import (get_algo_hidden_subset,
                                             get_algo_naked_subset,
                                             get_algo_find_single_candidates, get_algo_invalidate_solved_values,
                                             get_algo_invalidate_with_n_fish,
                                             get_algo_apply_skyscraper, get_algo_apply_x_chain, get_algo_apply_xy_chain,
                                             get_algo_xy_wing)
from sudoku_solver.board.board import Board
from sudoku_solver.puzzles.prefills import parse_sudoku, SUDOKU
from sudoku_solver.ui.ui import init_ui, run_ui_loop

if __name__ == '__main__':
    prefilled_values = parse_sudoku(SUDOKU)
    board = Board(prefilled_values=prefilled_values)

    # have board and ui in sync via observer pattern
    sudoku_ui = init_ui(prefilled_values=prefilled_values)
    board.substribe_observer_to_cells(observer_finishing_value=sudoku_ui.observe_finishing_value,
                                      observer_invalidating_candidate=sudoku_ui.observe_invalidating_candidate)
    board.subscribe_preview(observer_preview=sudoku_ui.observe_preview)

    sudoku_ui.add_algorithm(text="Invalidate solved Values",
                            handler=get_algo_invalidate_solved_values(board))
    sudoku_ui.add_algorithm(text="Find single candidates",
                            handler=get_algo_find_single_candidates(board))
    sudoku_ui.add_algorithm(text="Locked Candidate",
                            handler=get_algo_locked_candidate(board))
    sudoku_ui.add_algorithm(text="Naked Subset (Pair, Triple, Quadruple, Quintuple)",
                            handler=get_algo_naked_subset(board))
    sudoku_ui.add_algorithm(text="Hidden Subset (Pair, Triple, Quadruple, Quintuple)",
                            handler=get_algo_hidden_subset(board))
    sudoku_ui.add_algorithm(text="X-Wing (fish n=2)",
                            handler=get_algo_invalidate_with_n_fish(board, n=2))
    sudoku_ui.add_algorithm(text="Swordfish (fish n=3)",
                            handler=get_algo_invalidate_with_n_fish(board, n=3))
    sudoku_ui.add_algorithm(text="Jellyfish (fish n=4)",
                            handler=get_algo_invalidate_with_n_fish(board, n=4))
    sudoku_ui.add_algorithm(text="Squirmbag (fish n=5)",
                            handler=get_algo_invalidate_with_n_fish(board, n=5))
    sudoku_ui.add_algorithm(text="Whale (fish n=6)",
                            handler=get_algo_invalidate_with_n_fish(board, n=6))
    sudoku_ui.add_algorithm(text="Leviathan (fish n=7)",
                            handler=get_algo_invalidate_with_n_fish(board, n=7))
    sudoku_ui.add_algorithm(text="Skyscraper (Chain)",
                            handler=get_algo_apply_skyscraper(board))
    sudoku_ui.add_algorithm(text="X-Chain",
                            handler=get_algo_apply_x_chain(board))
    sudoku_ui.add_algorithm(text="XY-Chain",
                            handler=get_algo_apply_xy_chain(board))
    sudoku_ui.add_algorithm(text="Remote Pair",
                            handler=get_algo_remote_pair(board))
    sudoku_ui.add_algorithm(text="2-String Kite",
                            handler=get_algo_two_string_kite(board))
    sudoku_ui.add_algorithm(text="Empty Rectangle",
                            handler=get_algo_empty_rectangle(board))
    sudoku_ui.add_algorithm(text="XY-Wing",
                            handler=get_algo_xy_wing(board))
    sudoku_ui.add_algorithm(text="XYZ-Wing",
                            handler=get_algo_xyz_wing(board))
    sudoku_ui.add_algorithm(text="W-Wing",
                            handler=get_algo_w_wing(board))
    sudoku_ui.add_algorithm(text="Singly- or doubly-linked Almost-Locked Set",
                            handler=get_algo_singly_or_doubly_linked_als(board))
    sudoku_ui.add_algorithm(text="Discontinuous Nice Loop",
                            handler=get_algo_discontinuous_nice_loop(board))
    sudoku_ui.add_algorithm(text="Uniquene Rectangles (Types I, II, IV)",
                            handler=get_algo_uniqueness_violations(board))
    sudoku_ui.add_algorithm(text="Sue de Coq",
                            handler=get_algo_sue_de_coq(board))

    # stats = Stats(board)
    # print(f'Original Board')
    # stats.shout_current_status()
    board.validate_finished_board()

    # board.as_df(mode='candidates').to_clipboard()

    run_ui_loop(sudoku_ui=sudoku_ui)
