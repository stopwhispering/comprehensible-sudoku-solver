from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PrefilledValue:
    x: int
    y: int
    value: int


class SudokuPuzzle:
    def __init__(self, prefilled_values: List[PrefilledValue]):
        self.prefilled_values = prefilled_values

    def get(self, x: int, y: int) -> Optional[int]:
        values = [p for p in self.prefilled_values if p.x == x and p.y == y]
        if values:
            return values[0].value
