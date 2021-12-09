from sudoku_solver.board.board import Board


class Stats:

    def __init__(self, board: Board):
        self.board = board
        self.compare_solved: int = 0
        self.compare_unsolved: int = 0
        self.compare_remaining_candidates: int = 0

    def update_comparison_stats(self):
        self.compare_solved = self.board.get_count_solved()
        self.compare_unsolved = self.board.get_count_unsolved()
        self.compare_remaining_candidates = self.board.get_count_remaining_candidates()

    @property
    def has_changed(self):
        return (self.compare_solved != self.board.get_count_solved() or
                self.compare_unsolved != self.board.get_count_unsolved() or
                self.compare_remaining_candidates != self.board.get_count_remaining_candidates())

    def shout_current_status(self, after_step: str = ''):
        step = '' if not after_step else 'After: ' + after_step
        solved = self.board.get_count_solved()
        unsolved = self.board.get_count_unsolved()
        remaining_candidates = self.board.get_count_remaining_candidates()

        print(f'{step.ljust(65)} - Solved/Unsolved/Remaining Candidates: {solved}/{unsolved}/{remaining_candidates}')
