from typing import Tuple, Dict, List, Optional, Callable, Sequence
import tkinter
from tkinter import filedialog

from sudoku_solver.shared.constants import SUDOKU_DIR
from sudoku_solver.shared.preview import Preview, IndicatorLevel, PreviewArrow, HighlightedPosition
from sudoku_solver.shared.puzzle import SudokuPuzzle, ValuePosition, read_sudoku_file
from sudoku_solver.ui.coordinates import get_candidate_center_coords
from sudoku_solver.ui.rectangles import CandidateRectangle, ValueRectangle
from sudoku_solver.ui.ui_constants import (MARGIN, CELL_LENGTH, WIDTH, HEIGHT, PADDING_BETWEEN_BUTTONS, COLOR)


class SudokuUI(tkinter.Frame):
    def __init__(self, tk: tkinter.Tk):
        tkinter.Frame.__init__(self, master=tk)
        self.tk: tkinter.Tk = tk
        self.row, self.col = -1, -1
        self.tk.title("Sudoku - Comprehensible Algorithms Solver")
        self.pack(fill='both')

        self.canvas = tkinter.Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill=tkinter.BOTH, side=tkinter.LEFT)

        self.value_rectangles: Dict[Tuple[int, int], ValueRectangle] = {}
        # self.candidate_rectangles: Dict[Tuple[int, int, int], CandidateRectangle] = {}
        self.candidate_rectangles: Dict[ValuePosition, CandidateRectangle] = {}
        self._draw_grid()
        self._draw_candidates()

        self.previous_preview_ids: List[int] = []
        self.buttons: List[tkinter.Button] = []
        self.previous_button: Optional[tkinter.Button] = None
        self.previous_button_handler: Optional[Callable] = None
        self.cancel_button: Optional[tkinter.Button] = None

        self.algo_buttons_frame = tkinter.Frame(self)
        self.algo_buttons_frame.pack(side=tkinter.TOP, ipady=MARGIN)

        self.default_buttons_frame = tkinter.Frame(self)
        self.default_buttons_frame.pack(side=tkinter.BOTTOM, ipady=MARGIN)

        self.add_default_buttons()

    def set_algorithms(self, algorithms: List[Tuple[str, Callable]]) -> None:
        """define algorithm function with texts; buttons are created for each"""
        frame = None
        for i, algorithm in enumerate(algorithms):
            if not i % 13:
                frame = tkinter.Frame(self.algo_buttons_frame)
                frame.pack(side=tkinter.LEFT)  # , ipadx=20, ipady=10)

            self._add_algorithm(frame=frame, text=algorithm[0], handler=algorithm[1])

    def _add_algorithm(self, frame, text: str, handler: Callable):
        """add a button for supplied algorithm function"""

        def decorated_handler(*args, **kwargs):
            """remember last pressed button"""
            self.previous_button = btn
            handler(*args, **kwargs)

        btn = tkinter.Button(frame, text=text, command=decorated_handler)
        btn.pack(fill=tkinter.BOTH, side=tkinter.TOP, pady=PADDING_BETWEEN_BUTTONS, padx=PADDING_BETWEEN_BUTTONS)
        self.buttons.append(btn)

    def add_default_buttons(self):
        self.cancel_button = tkinter.Button(self.default_buttons_frame, text='Cancel', state='disabled', command='')
        self.cancel_button.pack(fill=tkinter.BOTH,
                                side=tkinter.LEFT,
                                padx=PADDING_BETWEEN_BUTTONS,
                                pady=PADDING_BETWEEN_BUTTONS)

        open_button = tkinter.Button(self.default_buttons_frame,
                                     text='Open Sudoku',
                                     command=self.show_select_file_dialog)
        open_button.pack(fill=tkinter.BOTH,
                         side=tkinter.RIGHT,
                         padx=PADDING_BETWEEN_BUTTONS,
                         pady=PADDING_BETWEEN_BUTTONS)

    def show_select_file_dialog(self):
        filename = filedialog.askopenfilename(initialdir=SUDOKU_DIR,
                                              defaultextension='.sudoku',
                                              filetypes=[('Sudoku Files', '*.sudoku')])
        if not filename:
            return
        sudoku = read_sudoku_file(path=filename)
        # todo separate modules
        from sudoku_solver.init import start_sudoku
        start_sudoku(sudoku=sudoku, running_ui=self)

    def prefill_values(self, prefilled_values: SudokuPuzzle):
        """set the original, known candidates"""
        for prefilled_value in prefilled_values.prefilled_values:
            value_rectangle = self.value_rectangles[(prefilled_value.y, prefilled_value.x)]
            value_rectangle.remove_grid_candidates_for_cell()
            value_rectangle.write_value_found(value=prefilled_value.value, color=COLOR.PREFILLED_VALUE_FONT)

    def _draw_grid(self):
        """draw the Sudoku grid, i.e. the lines demarcating the candidate rectangles;
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
        """create and draw all 9x9 candidate rectangles, each with 9 candidate sub-rectangles"""
        for x in range(1, 10):
            for y in range(1, 10):
                value_rectangle = ValueRectangle(y=y,
                                                 x=x,
                                                 canvas=self.canvas)
                self.value_rectangles[(y, x)] = value_rectangle

                for candidate in range(1, 10):
                    candidate_rectangle = CandidateRectangle(
                            candidate=candidate,
                            canvas=self.canvas,
                            value_rectangle=value_rectangle)
                    candidate_rectangle.paint_bg(color=COLOR.CANDIDATE_BG)
                    candidate_rectangle.write_candidate(color=COLOR.CANDIDATE_FONT)

                    self.candidate_rectangles[ValuePosition(x=x,
                                                            y=y,
                                                            value=candidate)] = candidate_rectangle

                    value_rectangle.candidate_rectangles[candidate] = candidate_rectangle

    def _draw_found_value(self, solved_value_position: ValuePosition):
        value_rectangle = self.value_rectangles[(solved_value_position.y, solved_value_position.x)]
        value_rectangle.remove_grid_candidates_for_cell()
        value_rectangle.write_value_found(value=solved_value_position.value, color=COLOR.FOUND_VALUE_FONT)

    def observe_finishing_value(self, solved_value_position: ValuePosition):
        """observer function for finished candidates from board;
        subscribe to board observer"""
        self._draw_found_value(solved_value_position)

    def observe_invalidating_candidate(self, invalidated_candidate_position: ValuePosition):
        """observer function for invalidated candidate candidates from board;
        subscribe to board observer"""
        candidate_rectangle = self.candidate_rectangles[invalidated_candidate_position]
        candidate_rectangle.remove_text()
        candidate_rectangle.paint_bg(COLOR.INVALID_CANDIDATE_BG)

    def _draw_preview_line(self, line_nodes: Sequence[ValuePosition]):
        for i in range(len(line_nodes) - 1):
            node_a = self.candidate_rectangles[line_nodes[i]]
            node_b = self.candidate_rectangles[line_nodes[i+1]]

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

    def _draw_preview_invalidations(self, invalidated_positions: Sequence[ValuePosition]):
        for position in invalidated_positions:
            candidate_rectangle = self.candidate_rectangles[ValuePosition(position.x, position.y, position.value)]
            preview_overlay = candidate_rectangle.paint_preview_overlay(color=COLOR.RED)
            self.previous_preview_ids.append(preview_overlay)

    @staticmethod
    def arrow_to_coords(arrow: PreviewArrow) -> Tuple[float, float, float, float]:
        x_from, y_from = get_candidate_center_coords(y=arrow.pos_from.y,
                                                     x=arrow.pos_from.x,
                                                     candidate=arrow.pos_from.value)
        x_to, y_to = get_candidate_center_coords(y=arrow.pos_to.y,
                                                 x=arrow.pos_to.x,
                                                 candidate=arrow.pos_to.value)
        return x_from, y_from, x_to, y_to

    def _draw_preview_arrows(self, indicator_arrows: Sequence[PreviewArrow]):
        for arrow in indicator_arrows:
            x0, y0, x1, y1 = self.arrow_to_coords(arrow)
            color = self._indicator_level_to_color(indicator_level=arrow.indicator_level).value
            preview_overlay = self.canvas.create_line(x0, y0, x1, y1, arrow=tkinter.LAST, fill=color)
            self.previous_preview_ids.append(preview_overlay)

    @staticmethod
    def _indicator_level_to_color(indicator_level: IndicatorLevel) -> COLOR:
        if indicator_level == IndicatorLevel.DEFAULT:
            return COLOR.GREEN
        elif indicator_level == IndicatorLevel.FIRST:
            return COLOR.CYAN
        elif indicator_level == IndicatorLevel.LAST:
            return COLOR.RED
        elif indicator_level == IndicatorLevel.ALTERNATIVE:
            return COLOR.BLUE
        else:
            raise ValueError('Unknown IndicatorLevel. Map to Color.')

    def _draw_preview_indications(self, indicated_positions: Sequence[HighlightedPosition]):
        for position in indicated_positions:
            if not position.indicator_level:
                color = COLOR.GREEN
            else:
                color = self._indicator_level_to_color(indicator_level=position.indicator_level)

            candidate_rectangle = self.candidate_rectangles[position]
            preview_overlay = candidate_rectangle.paint_preview_overlay(color=color)
            self.previous_preview_ids.append(preview_overlay)

    def observe_preview(self, preview: Preview):
        line_nodes = preview.get_preview_line_nodes()
        if line_nodes:
            self._draw_preview_line(line_nodes=line_nodes)

        invalidated_positions = preview.get_invalidated_candidates()
        if invalidated_positions:
            self._draw_preview_invalidations(invalidated_positions=invalidated_positions)

        indicator_candidates = preview.get_indicator_candidates()
        if indicator_candidates:
            self._draw_preview_indications(indicated_positions=indicator_candidates)

        indicator_arrows = preview.get_indicator_arrows()
        if indicator_arrows:
            self._draw_preview_arrows(indicator_arrows=indicator_arrows)

        self.start_preview_mode(execute_fn=preview.execute)

    def start_preview_mode(self, execute_fn: Callable):
        """stat preview mode: hide algo buttons, show only ok/cancel buttons; supply function to be executed
        upon hitting ok btn"""
        for btn in [b for b in self.buttons if b is not self.previous_button]:
            btn.config(state="disabled")

        self.cancel_button.config(state="normal", command=self.end_preview_mode)
        self.previous_button_handler = self.previous_button['command']
        self.previous_button.config(command=lambda: (self.end_preview_mode(), execute_fn()),
                                    bg='blue')

    def end_preview_mode(self):
        """end preview mode: hide preview widgets/overlays; disable ok/cancel buttons; enable algo buttons"""
        while self.previous_preview_ids:
            self.canvas.delete(self.previous_preview_ids.pop())

        for btn in self.buttons:
            btn.config(state="normal")
        self.cancel_button.config(state="disabled", command='')
        self.previous_button.config(command=self.previous_button_handler,  # string-encoded; seems to work though
                                    bg='SystemButtonFace')  # default grey
