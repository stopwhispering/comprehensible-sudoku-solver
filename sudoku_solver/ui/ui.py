from typing import Tuple, Dict, List, Optional, Callable
import tkinter

from sudoku_solver.solver.artefacts import Artefact, IndicatorLevel
from sudoku_solver.ui.rectangles import CandidateRectangle, ValueRectangle
from sudoku_solver.ui.ui_constants import (MARGIN, CELL_LENGTH, WIDTH, HEIGHT, BUTTONS_WIDTH,
                                           PADDING_BETWEEN_BUTTONS, COLOR)


class SudokuUI(tkinter.Frame):
    def __init__(self, tk):
        tkinter.Frame.__init__(self, master=tk)
        self.tk = tk
        self.row, self.col = -1, -1
        self.tk.title("Sudoku - Comprehensible Algorithms Solver")
        self.pack(fill='both')

        self.canvas = tkinter.Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill=tkinter.BOTH, side=tkinter.LEFT)

        self.value_rectangles: Dict[Tuple[int, int], ValueRectangle] = {}
        self.candidate_rectangles: Dict[Tuple[int, int, int], CandidateRectangle] = {}
        self._draw_grid()
        self._draw_candidates()

        self.previous_preview_ids: List[int] = []
        self.buttons: List[tkinter.Button] = []
        self.previous_button: Optional[tkinter.Button] = None
        self.previous_button_handler: Optional[Callable] = None
        self.cancel_button: Optional[tkinter.Button] = None

        self.add_default_buttons()

    def add_algorithm(self, text: str, handler: callable):
        """add a button for supplied algorithm function"""

        def decorated_handler(*args, **kwargs):
            # remember last pressed button
            self.previous_button = btn
            handler(*args, **kwargs)

        btn = tkinter.Button(self, text=text, command=decorated_handler)
        btn.pack(fill=tkinter.BOTH, side=tkinter.TOP, pady=PADDING_BETWEEN_BUTTONS)
        self.buttons.append(btn)

    def add_default_buttons(self):
        self.cancel_button = tkinter.Button(self, text='Cancel', state='disabled', command=None)
        self.cancel_button.pack(fill=tkinter.BOTH, side=tkinter.BOTTOM, pady=PADDING_BETWEEN_BUTTONS)

    def prefill_values(self, prefilled_values: Dict[Tuple, int]):
        """set the original, known values"""
        for position, value in prefilled_values.items():
            x, y = position
            value_rectangle = self.value_rectangles[(x, y)]
            value_rectangle.remove_grid_candidates_for_cell()
            value_rectangle.write_value_found(value=value, color=COLOR.PREFILLED_VALUE_FONT)

    def _draw_grid(self):
        """draw the Sudoku grid, i.e. the lines demarcating the value rectangles;
        this grid is permanent, so we don't need to remember any line ids"""
        for i in range(10):
            color = "blue" if i % 3 == 0 else "gray"
            # vertical lines
            x0 = x1 = MARGIN + i * CELL_LENGTH
            y0 = MARGIN
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)
            # horizontal lines
            x0 = MARGIN
            x1 = WIDTH - MARGIN
            y0 = y1 = MARGIN + i * CELL_LENGTH
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    def _draw_candidates(self):
        """create and draw all 9x9 value rectangles, each with 9 candidate sub-rectangles"""
        for x in range(9):
            for y in range(9):
                value_rectangle = ValueRectangle(x=x,
                                                 y=y,
                                                 canvas=self.canvas)
                self.value_rectangles[(x, y)] = value_rectangle

                for n in range(9):
                    candidate = n + 1
                    candidate_rectangle = CandidateRectangle(
                            candidate=candidate,
                            canvas=self.canvas,
                            value_rectangle=value_rectangle)
                    candidate_rectangle.paint_bg(color=COLOR.CANDIDATE_BG)
                    candidate_rectangle.write_candidate(color=COLOR.CANDIDATE_FONT)

                    self.candidate_rectangles[(x, y, candidate,)] = candidate_rectangle
                    value_rectangle.candidate_rectangles[candidate] = candidate_rectangle

    def _draw_found_value(self, x: int, y: int, value: int):
        value_rectangle = self.value_rectangles[(x, y)]
        value_rectangle.remove_grid_candidates_for_cell()
        value_rectangle.write_value_found(value=value, color=COLOR.FOUND_VALUE_FONT)

    def observe_finishing_value(self, x, y, value):
        """observer function for finished values from board;
        subscribe to board observer"""
        self._draw_found_value(x=int(x), y=int(y), value=int(value))

    def observe_invalidating_candidate(self, x, y, invalidated_value):
        """observer function for invalidated candidate values from board;
        subscribe to board observer"""
        candidate_rectangle = self.candidate_rectangles[(x, y, invalidated_value)]
        candidate_rectangle.remove_text()
        candidate_rectangle.paint_bg(COLOR.INVALID_CANDIDATE_BG)

    def _draw_preview_line(self, line_nodes: Tuple[Tuple[int, int, int]]):
        for i in range(len(line_nodes) - 1):
            node_a = self.candidate_rectangles[(line_nodes[i][0],
                                                line_nodes[i][1],
                                                line_nodes[i][2],)]

            node_b = self.candidate_rectangles[(line_nodes[i + 1][0],
                                                line_nodes[i + 1][1],
                                                line_nodes[i + 1][2],)]
            x0 = min(node_a.ui_coords[0], node_b.ui_coords[0])
            y0 = min(node_a.ui_coords[1], node_b.ui_coords[1])
            x1 = max(node_a.ui_coords[2], node_b.ui_coords[2])
            y1 = max(node_a.ui_coords[3], node_b.ui_coords[3])
            coords = (x0, y0, x1, y1)
            green_rectangle = self.canvas.create_rectangle(*coords,
                                                           fill='green',
                                                           width=2,
                                                           outline="green",
                                                           stipple="gray12")  # "gray50"
            self.previous_preview_ids.append(green_rectangle)

    def _draw_preview_invalidations(self, invalidated_positions: Tuple[Tuple[int, int, int]]):
        for position in invalidated_positions:
            candidate_rectangle = self.candidate_rectangles[(position[0], position[1], position[2])]
            preview_overlay = candidate_rectangle.paint_preview_overlay(color=COLOR.RED)
            self.previous_preview_ids.append(preview_overlay)

    def _draw_preview_indications(self, indicated_positions: Tuple[Tuple[int, int, int, Optional[IndicatorLevel]]]):
        for position in indicated_positions:
            # todo: central mapping from level to color
            if len(position) < 4 or position[3] == IndicatorLevel.DEFAULT:
                color = COLOR.GREEN
            elif position[3] == IndicatorLevel.FIRST:
                color = COLOR.BLUE
            elif position[3] == IndicatorLevel.LAST:
                color = COLOR.BLUE
            elif position[3] == IndicatorLevel.ALTERNATIVE:
                color = COLOR.CYAN
            else:
                raise ValueError('Unknown IndicatorLevel. Map to Color.')

            candidate_rectangle = self.candidate_rectangles[(position[0], position[1], position[2])]
            preview_overlay = candidate_rectangle.paint_preview_overlay(color=color)
            self.previous_preview_ids.append(preview_overlay)

    def observe_preview(self, preview: Artefact):
        line_nodes = preview.get_preview_line_nodes()
        if line_nodes:
            self._draw_preview_line(line_nodes=line_nodes)

        invalidated_positions = preview.get_invalidated_candidates()
        if invalidated_positions:
            self._draw_preview_invalidations(invalidated_positions=invalidated_positions)

        indicator_candidates = preview.get_indicator_candidates()
        if indicator_candidates:
            self._draw_preview_indications(indicated_positions=indicator_candidates)

        self.start_preview_mode(execute_fn=preview.execute)

    def start_preview_mode(self, execute_fn: Callable):
        """stat preview mode: hide algo buttons, show only ok/cancel buttons; supply function to be executed
        upon hitting ok btn"""
        for btn in [b for b in self.buttons if b is not self.previous_button]:
            btn.config(state="disabled")

        self.cancel_button.config(state="normal", command=self.end_preview_mode)
        self.previous_button_handler = self.previous_button['command']  # todo works?
        self.previous_button.config(command=lambda: (self.end_preview_mode(), execute_fn()),
                                    bg='blue')

    def end_preview_mode(self):
        """end preview mode: hide preview widgets/overlays; disable ok/cancel buttons; enable algo buttons"""
        while self.previous_preview_ids:
            self.canvas.delete(self.previous_preview_ids.pop())

        for btn in self.buttons:
            btn.config(state="normal")
        self.cancel_button.config(state="disabled", command=None)
        self.previous_button.config(command=self.previous_button_handler,  # string-encoded; seems to work though
                                    bg='SystemButtonFace')  # default grey


def init_ui(prefilled_values: Dict[Tuple, int]) -> SudokuUI:
    tk = tkinter.Tk()
    sudoku_ui = SudokuUI(tk)
    sudoku_ui.prefill_values(prefilled_values)
    return sudoku_ui


def run_ui_loop(sudoku_ui: SudokuUI):
    sudoku_ui.tk.geometry(f'{WIDTH + BUTTONS_WIDTH}x{HEIGHT}')
    sudoku_ui.tk.mainloop()
