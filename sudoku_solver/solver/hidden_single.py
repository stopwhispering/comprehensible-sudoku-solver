from sudoku_solver.board.board import Board
from sudoku_solver.solver.decorators import evaluate_algorithm


@evaluate_algorithm
def find_hidden_single(board: Board):
    """
    simple solver: if in a row, col, or block, only one cell has a specific candidate, we can set that cell/candidate as
    solved
    """
    for unit in board.get_all_houses():
        unit.solve_single_candidates()