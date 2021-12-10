from typing import Dict, Tuple

# # not solved, yet
# SUDOKU = (
#     '       2 ',
#     '  64  13 ',
#     '4   9    ',
#     '   1    2',
#     '  8     9',
#     ' 3  7 81 ',
#     '  39  64 ',
#     '        8',
#     ' 7   5   ',
#     )

# "extreme" (difficult but solved)
SUDOKU = (
    '',
    ' 186  45',
    ' 2 4   3',
    '    1 38',
    '   3 7',
    ' 57 6',
    ' 9   8 6',
    ' 86  514',
    '',
    )


# # "evil" (difficult but solved)
# SUDOKU = (
#     '   1    7',
#     '  8 4  9',
#     ' 7   36',
#     '9    85',
#     ' 3  9  8',
#     '  43    1',
#     '  34   2',
#     ' 9  8 3',
#     '5    1',
# )

# # medium, simpler algos suffice
# SUDOKU = (
#     '5  76 34',
#     '7    9',
#     '6 32  7',
#     '    4  85',
#     '',
#     '47  1',
#     '  7  25 1',
#     '   6    3',
#     ' 96 75  4',
# )


# # difficult but solved
# SUDOKU = (
#     '5    38 6',
#     '6  1 9',
#     '    4 1',
#     '9      5',
#     ' 4    72',
#     ' 8   1 34',
#     '  7 5  6',
#     '   8  2',
#     '',
#     )

# # easy
# SUDOKU = (
#     '9',
#     '     1  7',
#     '5    3  4',
#     '  7   2',
#     '  36 8',
#     '   4  61',
#     ' 85 4',
#     '   32  6',
#     ' 4  1  9'
#     )

# # easy
# SUDOKU = (
#     ' 127     ',
#     ' 7 6 8   ',
#     '      83 ',
#     '  8  7   ',
#     '      35 ',
#     '  6  4   ',
#     '24       ',
#     '    5  16',
#     '1   8 9  ',
#     )

# # easy
# SUDOKU = (
#     '16       ',
#     '8   43  5',
#     '   6   31',
#     '    7    ',
#     '   9 1   ',
#     '5 7  426 ',
#     '  93  8  ',
#     '758  9 4 ',
#     '     6 5 ',
#     )


def parse_sudoku(sudoku: tuple) -> Dict[Tuple, int]:
    prefilled = {}
    assert (len(sudoku) == 9)
    for i, row in enumerate(sudoku):
        for x, c in enumerate(row):
            if c in '123456789':
                y = 8 - i
                prefilled[(x, y)] = int(c)

    return prefilled
