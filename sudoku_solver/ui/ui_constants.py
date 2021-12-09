from enum import Enum

MARGIN = 20  # px around board
CELL_LENGTH = 60  # width of every board cell.
WIDTH = HEIGHT = MARGIN * 2 + CELL_LENGTH * 9  # Width and height of the whole board
BUTTONS_WIDTH = 450
CANDIDATE_LENGTH = CELL_LENGTH / 3
VALUE_FONT_SIZE = 36
CANDIDATE_FONT_SIZE = 10
PADDING_BETWEEN_BUTTONS = 4


class COLOR(Enum):
    INVALID_CANDIDATE_BG = '#aaaaaa'
    CANDIDATE_BG = '#dddddd'
    FOUND_VALUE_FONT = 'sea green'
    PREFILLED_VALUE_FONT = 'black'
    CANDIDATE_FONT = 'grey'
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    CYAN = 'cyan'
