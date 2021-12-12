from sudoku_solver.solver.almost_locked_sets import find_singly_or_doubly_linked_als
from sudoku_solver.solver.empty_rectangle import find_empty_rectangle
from sudoku_solver.solver.nice_loop import find_nice_loop
from sudoku_solver.solver.sue_de_coq import find_sue_de_coq
from sudoku_solver.solver.two_string_kite import find_two_string_kite
from sudoku_solver.solver.remote_pair import find_remote_pair
from sudoku_solver.board.board import Board
from sudoku_solver.solver.chains import find_xy_chain, find_x_chain
from sudoku_solver.solver.fish import find_n_fish
from sudoku_solver.solver.hidden_subset import find_hidden_subset
from sudoku_solver.solver.naked_subset import find_naked_subset
from sudoku_solver.solver.locked_candidate import find_locked_candidate
from sudoku_solver.solver.skyscraper import find_skyscraper
from sudoku_solver.solver.uniqueness import find_uniqueness_violations
from sudoku_solver.solver.w_wing import find_w_wing
from sudoku_solver.solver.xy_z_wing import find_xy_wing, find_xyz_wing

# todo decorate instead of reapeating....

def get_algo_invalidate_solved_values(board: Board):
    """
    simple invalidator: iterate through rows, cols, packages and invalidate yet-solved candidates
    """
    def invalidate_solved_values():
        for unit in board.get_all_houses():
            unit.invalidate_solved_values()
        board.validate_consistency_in_all_houses()

    return invalidate_solved_values


def get_algo_find_single_candidates(board: Board):
    """
    simple solver: if in a row, col, or block, only one cell has a specific candidate, we can set that cell/candidate as
    solved
    """

    def find_single_candidates():
        for unit in board.get_all_houses():
            unit.solve_single_candidates()
        board.validate_consistency_in_all_houses()

    return find_single_candidates


def get_algo_naked_subset(board: Board):
    """if three cells together share the same 3 candidates (although they don't need to have them all),
    then we can rule these candidates out for other cells of the unit. Example:
    (39), (59), (359) -> other cells may not have 359"""
    def identify_naked_subset():
        get_algo_invalidate_solved_values(board=board)()
        find_naked_subset(board=board)
        board.validate_consistency_in_all_houses()
    return identify_naked_subset


def get_algo_locked_candidate(board: Board):
    """in a house, look for all cells having a specific candidate
       a. if we're in a box, test if all these cells are in a single row or column
       b. if we're in a row/col, test if all these cells are in a single box
    if true, we can invalidate that candidate for...
       a. other cells in that row or column
       b. other cells in that box
    """
    def identify_find_locked_candidate():
        get_algo_invalidate_solved_values(board=board)()
        find_locked_candidate(board=board)
        board.validate_consistency_in_all_houses()
    return identify_find_locked_candidate


def get_algo_hidden_subset(board: Board):
    """if three candidate candidates are valid for only three cells (although they
    don't need to each have all of them),
    then we can rule out all other candidate candidates for these cells. Example:
    123 are candidates for only 1357, 1259, 2357 -> make them 13, 12, 23"""
    def identify_hidden_subset():
        get_algo_invalidate_solved_values(board=board)()
        find_hidden_subset(board=board)
        board.validate_consistency_in_all_houses()
    return identify_hidden_subset


def get_algo_invalidate_with_n_fish(board: Board, n: int):
    """
    If n (e.g. 3) rows exist in which the candidate under consideration occurs only in exactly the same n different
    columns (either in all those columns or in two of them), then we have found a fish (3 -> swordfish). We may then
    invalidate the candidate in all other cells of those columns. (cf. x-wing)
    n = 3 --> swordfish
    n = 4 --> jellyfish
    n = 5 --> squirmbag
    n = 6 --> whale
    n = 7 --> leviathan
    """
    def identify_n_fish():
        get_algo_invalidate_solved_values(board=board)()
        find_n_fish(board=board, n=n)
        board.validate_consistency_in_all_houses()
    return identify_n_fish


def get_algo_apply_skyscraper(board: Board):
    """apply the skyscraper logic (version of turbot fish)"""
    def identify_skyscraper():
        get_algo_invalidate_solved_values(board=board)()
        find_skyscraper(board=board)
        board.validate_consistency_in_all_houses()
    return identify_skyscraper


def get_algo_apply_x_chain(board: Board):
    """apply the x-chain logic"""
    def identify_x_chain():
        get_algo_invalidate_solved_values(board=board)()
        find_x_chain(board=board)
        board.validate_consistency_in_all_houses()
    return identify_x_chain


def get_algo_apply_xy_chain(board: Board):
    """apply the xy-chain logic"""
    def identify_xy_chain():
        get_algo_invalidate_solved_values(board=board)()
        find_xy_chain(board=board)
        board.validate_consistency_in_all_houses()
    return identify_xy_chain


def get_algo_discontinuous_nice_loop(board: Board):
    """apply the discontinuous nice loop logic"""
    def identify_discontinuous_nice_loop():
        get_algo_invalidate_solved_values(board=board)()
        find_nice_loop(board=board)
        board.validate_consistency_in_all_houses()
    return identify_discontinuous_nice_loop


def get_algo_remote_pair(board: Board):
    """find remote-pair algorithm (similar to x-chain
    and xy-chain)"""
    def identify_remote_pair():
        get_algo_invalidate_solved_values(board=board)()
        find_remote_pair(board=board)
        board.validate_consistency_in_all_houses()
    return identify_remote_pair


def get_algo_two_string_kite(board: Board):
    """find 2-string kite algorithm (similar to x-chain)"""
    def identify_two_string_kite():
        get_algo_invalidate_solved_values(board=board)()
        find_two_string_kite(board=board)
        board.validate_consistency_in_all_houses()
    return identify_two_string_kite


def get_algo_xy_wing(board: Board):
    """find xy-wing algorithm (similar to xy-chain)"""
    def identify_xy_wing():
        get_algo_invalidate_solved_values(board=board)()
        find_xy_wing(board=board)
        board.validate_consistency_in_all_houses()
    return identify_xy_wing


def get_algo_xyz_wing(board: Board):
    """find xyz-wing algorithm (similar to xy-wing)"""
    def identify_xyz_wing():
        get_algo_invalidate_solved_values(board=board)()
        find_xyz_wing(board=board)
        board.validate_consistency_in_all_houses()
    return identify_xyz_wing


def get_algo_singly_or_doubly_linked_als(board: Board):
    """find singly- or doubly-linked almost-locked-set algorithm"""
    def identify_singly_or_doubly_linked_als():
        get_algo_invalidate_solved_values(board=board)()
        find_singly_or_doubly_linked_als(board=board)
        board.validate_consistency_in_all_houses()
    return identify_singly_or_doubly_linked_als


def get_algo_w_wing(board: Board):
    """find w-wing algorithm"""
    def identify_w_wing():
        get_algo_invalidate_solved_values(board=board)()
        find_w_wing(board=board)
        board.validate_consistency_in_all_houses()
    return identify_w_wing


def get_algo_uniqueness_violations(board: Board):
    """find uniqueness violations algorithm (unique rectangle types)"""
    def identify_uniqueness_violations():
        get_algo_invalidate_solved_values(board=board)()
        find_uniqueness_violations(board=board)
        board.validate_consistency_in_all_houses()
    return identify_uniqueness_violations


def get_algo_sue_de_coq(board: Board):
    """find sue de coq algorithm"""
    def identify_sue_de_coq():
        get_algo_invalidate_solved_values(board=board)()
        find_sue_de_coq(board=board)
        board.validate_consistency_in_all_houses()
    return identify_sue_de_coq


def get_algo_empty_rectangle(board: Board):
    """find empty rectangle algorithm"""
    def identify_empty_rectangle():
        get_algo_invalidate_solved_values(board=board)()
        find_empty_rectangle(board=board)
        board.validate_consistency_in_all_houses()
    return identify_empty_rectangle