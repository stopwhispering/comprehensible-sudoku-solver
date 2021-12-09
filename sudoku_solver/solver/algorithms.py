from sudoku_solver.board.board import Board
from sudoku_solver.solver.chains import find_xy_chain, find_x_chain
from sudoku_solver.solver.fish import find_n_fish
from sudoku_solver.solver.hidden_subset import find_hidden_subset
from sudoku_solver.solver.naked_subset import find_naked_subset
from sudoku_solver.solver.skyscraper import find_skyscraper


def get_algo_invalidate_solved_values(board: Board):
    """
    simple invalidator: iterate through rows, cols, packages and invalidate yet-solved values
    """

    def invalidate_solved_values():
        for unit in board.get_all_houses():
            unit.invalidate_solved_values()
        board.validate_consistency_in_all_houses()

    return invalidate_solved_values


def get_algo_find_single_candidates(board: Board):
    """
    simple solver: if in a row, col, or block, only one cell has a specific candidate, we can set that cell/value as
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


def get_algo_hidden_subset(board: Board):
    """if three candidate values are valid for only three cells (although they
    don't need to each have all of them),
    then we can rule out all other candidate values for these cells. Example:
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
