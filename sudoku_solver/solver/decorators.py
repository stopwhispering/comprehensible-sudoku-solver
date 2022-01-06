from typing import Callable

# to be injected upon board instantiation
board_cache = {}


def evaluate_algorithm(func) -> Callable:
    """decorator for algorithms; evaluate consistency of board after applying, check if finished
    note: see init on how to bind to current board object"""
    def inner(*args, **kwargs):
        board = board_cache['current']
        kwargs['board'] = board
        func(*args, **kwargs)
        board.validate_consistency_in_all_houses()
        board.validate_finished_board()
    return inner
