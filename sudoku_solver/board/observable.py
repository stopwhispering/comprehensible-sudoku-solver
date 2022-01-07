from __future__ import annotations
from typing import TYPE_CHECKING

from sudoku_solver.shared.puzzle import ValuePosition

if TYPE_CHECKING:
    from sudoku_solver.shared.preview import Preview


class SudokuObservable:
    def __init__(self):
        self.observers_finished_values = []
        self.observers_invalidated_candidates = []
        self.observers_previews = []

    def subscribe_to_finished_values(self, observer: callable):
        if observer not in self.observers_finished_values:
            self.observers_finished_values.append(observer)

    def subscribe_to_invalidated_candidates(self, observer: callable):
        if observer not in self.observers_invalidated_candidates:
            self.observers_invalidated_candidates.append(observer)

    def subscribe_to_previews(self, observer_preview: callable):
        """subscribe to receive preview objects of type Preview to indicate pattern; they include
         an execute-function that actually executes finishing/invalidating of candidates"""
        if observer_preview not in self.observers_previews:
            self.observers_previews.append(observer_preview)

    def notify_solved_value(self, solved_value_position: ValuePosition):
        for observer in self.observers_finished_values:
            observer(solved_value_position)

    def notify_invalidated_candidate(self, invalidated_candidate_position: ValuePosition):
        for observer in self.observers_invalidated_candidates:
            observer(invalidated_candidate_position=invalidated_candidate_position)

    def notify_preview(self, preview: Preview):
        for observer in self.observers_previews:
            observer(preview)
