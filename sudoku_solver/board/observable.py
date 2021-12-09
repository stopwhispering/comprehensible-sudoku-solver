from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sudoku_solver.solver.artefacts import Artefact


class SudokuObservable:
    def __init__(self):
        self.observers_finishing_value = []
        self.observers_invalidating_candidate = []

        self.observers_preview = []

    def observe_finishing_value(self, observer: callable):
        if observer not in self.observers_finishing_value:
            self.observers_finishing_value.append(observer)

    def observe_invalidating_candidate(self, observer: callable):
        if observer not in self.observers_invalidating_candidate:
            self.observers_invalidating_candidate.append(observer)

    def subscribe_preview(self, observer_preview: callable):
        """subscribe to receive preview objects of type Artefact to indicate pattern; they include
        an execute() fn"""
        if observer_preview not in self.observers_preview:
            self.observers_preview.append(observer_preview)

    def notify_finishing_value(self, x: int, y: int, value: int):
        for observer in self.observers_finishing_value:
            observer(x, y, value)

    def notify_invalidating_candidate(self, x: int, y: int, invalidated_value: int):
        for observer in self.observers_invalidating_candidate:
            observer(x, y, invalidated_value)

    def notify_preview(self, preview: Artefact):
        for observer in self.observers_preview:
            observer(preview)
