from __future__ import annotations
from dataclasses import dataclass, field
import tkinter
from typing import Tuple, Dict

from sudoku_solver.ui.coordinates import get_candidate_rectangle_coords, board_position_to_coords
from sudoku_solver.ui.ui_constants import COLOR, CANDIDATE_FONT_SIZE, VALUE_FONT_SIZE


@dataclass
class CandidateRectangle:
    candidate: int
    canvas: tkinter.Canvas
    value_rectangle: ValueRectangle
    possible: bool = True
    id_bg_color: int = None
    id_text: int = None

    @property
    def n(self) -> int:
        return self.candidate

    @property
    def x(self) -> int:
        return self.value_rectangle.x

    @property
    def y(self) -> int:
        return self.value_rectangle.y

    @property
    def ui_coords(self) -> Tuple[float, float, float, float]:
        """return edges: x0, y0, x1, y1"""
        return get_candidate_rectangle_coords(y=self.y, x=self.x, candidate=self.candidate)

    def paint_bg(self, color: COLOR):
        self.remove_bg()
        self.id_bg_color = self.canvas.create_rectangle(*self.ui_coords, fill=color.value, width=0)

    def paint_preview_overlay(self, color: COLOR) -> int:
        return self.canvas.create_rectangle(*self.ui_coords,
                                            fill=color.value,
                                            stipple="gray50",
                                            width=2,
                                            outline="red")

    def remove_bg(self):
        if self.id_bg_color:
            self.canvas.delete(self.id_bg_color)

    def write_candidate(self, color: COLOR):
        self.remove_text()
        x0, y0, x1, y1 = self.ui_coords
        x_text = (x0 + x1) / 2
        y_text = (y0 + y1) / 2
        self.id_text = self.canvas.create_text(x_text, y_text,
                                               text=str(self.candidate),
                                               fill=color.value,
                                               font=tkinter.font.Font(size=CANDIDATE_FONT_SIZE, weight='normal'))

    def remove_text(self):
        if self.id_text:
            self.canvas.delete(self.id_text)


@dataclass
class ValueRectangle:
    y: int
    x: int
    canvas: tkinter.Canvas
    candidate_rectangles: Dict[int, CandidateRectangle] = field(default_factory=dict)  # wtf dataclasses...?!

    @property
    def ui_center_coords(self) -> Tuple[float, float]:
        """return pixel position of rectangle center (for writing text)"""
        return board_position_to_coords(self.y, self.x)

    def remove_grid_candidates_for_cell(self):
        # remove all candidate sub-rectangles, i.e. remove bg color and text
        for candidate_rectangle in self.candidate_rectangles.values():
            candidate_rectangle.remove_bg()
            candidate_rectangle.remove_text()
            candidate_rectangle.possible = False

    def write_value_found(self, value: int, color: COLOR):
        pos_y, pos_x = self.ui_center_coords
        self.canvas.create_text(pos_x,
                                pos_y,
                                text=value,
                                fill=color.value,
                                font=tkinter.font.Font(size=VALUE_FONT_SIZE, weight='bold'))
