from typing import Callable, Tuple, List

from sudoku_solver.board.board import Board
from sudoku_solver.solver.fish import find_n_fish
from sudoku_solver.solver.almost_locked_sets import find_singly_or_doubly_linked_als
from sudoku_solver.solver.chains import find_x_chain, find_xy_chain
from sudoku_solver.solver.empty_rectangle import find_empty_rectangle
from sudoku_solver.solver.hidden_single import find_hidden_single
from sudoku_solver.solver.hidden_subset import find_hidden_subset
from sudoku_solver.solver.locked_candidate import find_locked_candidate
from sudoku_solver.solver.naked_subset import find_naked_subset
from sudoku_solver.solver.nice_loop import find_nice_loop
from sudoku_solver.solver.remote_pair import find_remote_pair
from sudoku_solver.solver.skyscraper import find_skyscraper
from sudoku_solver.solver.sue_de_coq import find_sue_de_coq
from sudoku_solver.solver.two_string_kite import find_two_string_kite
from sudoku_solver.solver.uniqueness import find_uniqueness_violations
from sudoku_solver.solver.w_wing import find_w_wing
from sudoku_solver.solver.xy_z_wing import find_xyz_wing, find_xy_wing


def get_algo_invalidate_solved_values(board: Board):
    """
    simple invalidator: iterate through rows, cols, packages and invalidate already-solved candidates
    """
    def invalidate_solved_values():
        for unit in board.get_all_houses():
            unit.invalidate_solved_values()
        board.validate_consistency_in_all_houses()
        # board.validate_finished_board()

    return invalidate_solved_values


def get_fish_algorithm(board: Board, n: int):
    """
    n = 3 --> swordfish
    n = 4 --> jellyfish
    n = 5 --> squirmbag
    n = 6 --> whale
    n = 7 --> leviathan
    """
    def identify_n_fish():
        # get_algo_invalidate_solved_values(board=board)()
        find_n_fish(board=board, n=n)
    return identify_n_fish


def get_algorithms(board: Board) -> List[Tuple[str, Callable]]:
    algorithms = [
        ("Invalidate solved Values", get_algo_invalidate_solved_values(board)),
        ("Find hidden Singles", find_hidden_single),
        ("Locked Candidate", find_locked_candidate),
        ("Naked Subset (Pair, Triple, Quadruple, Quintuple)", find_naked_subset),
        ("Hidden Subset (Pair, Triple, Quadruple, Quintuple)", find_hidden_subset),
        ("X-Wing (fish n=2)", get_fish_algorithm(board, n=2)),
        ("Swordfish (fish n=3)", get_fish_algorithm(board, n=3)),
        ("Jellyfish (fish n=4)", get_fish_algorithm(board, n=4)),
        ("Squirmbag (fish n=5)", get_fish_algorithm(board, n=5)),
        ("Whale (fish n=6)", get_fish_algorithm(board, n=6)),
        ("Leviathan (fish n=7)", get_fish_algorithm(board, n=7)),
        ("Skyscraper (Chain)", find_skyscraper),
        ("X-Chain", find_x_chain),
        ("XY-Chain", find_xy_chain),
        ("Remote Pair", find_remote_pair),
        ("2-String Kite", find_two_string_kite),
        ("Empty Rectangle", find_empty_rectangle),
        ("XY-Wing", find_xy_wing),
        ("XYZ-Wing", find_xyz_wing),
        ("W-Wing", find_w_wing),
        ("Singly- or doubly-linked Almost-Locked Set", find_singly_or_doubly_linked_als),
        ("Discontinuous Nice Loop", find_nice_loop),
        ("Uniquene Rectangles (Types I, II, IV)", find_uniqueness_violations),
        ("Sue de Coq", find_sue_de_coq),
        ]
    return algorithms