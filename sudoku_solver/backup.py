#
# class StrongLinkSingleCell:
#     def __init__(self, cell: Cell, candidates: Tuple[int, int]):
#         assert len(candidates) == 2 and cell.has_candidate(candidates[0]) and cell.has_candidate(candidates[1])
#         self.cell = cell
#         self.candidates = candidates
#
#     def __str__(self):
#         return f'{repr(self.cell)}({self.candidates[0]}⇔{self.candidates[1]})'
#
#
# class WeakLinkSingleCell:
#     def __init__(self, cell: Cell, candidates: Tuple[int, int]):
#         assert len(candidates) == 2 and cell.has_candidate(candidates[0]) and cell.has_candidate(candidates[1])
#         self.cell = cell
#         self.candidates = candidates
#
#     def __str__(self):
#         return f'{repr(self.cell)}({self.candidates[0]}↔{self.candidates[1]})'
#
#

    # def link_ends_in_contradiction(self, new_link: Link):
    #     """todo required?????"""
    #     # todo remove
    #     @dataclass
    #     class Fiction:
    #         cell: Cell
    #         value: int = None
    #         invalidated_candidate: int = None
    #
    #     # cells = [cell for link in self.links for cell in link.cells]
    #     fictions: Dict[Cell, Fiction] = {}
    #     first_link = self.links[0]
    #     node = first_link.cells[0]
    #     assert new_link.cells[1] is first_link.cells[0]
    #     first = Fiction(cell=first_link.cells[0],
    #                     value=first_link.candidate if type(first_link) is WeakLink else None,
    #                     invalidated_candidate=first_link.candidate if type(first_link) is StrongLink else None)
    #     fictions[first_link.cells[0]] = first
    #
    #     for link in self.links:
    #         fiction = Fiction(cell=link.cells[1],
    #                           value=link.candidate if type(first_link) is StrongLink else None,
    #                           invalidated_candidate=first_link.candidate if type(first_link) is WeakLink else None)
    #         assert link.cells[1] not in fictions
    #         fictions[link.cells[1]] = fiction
    #
    #     new_fiction = Fiction(cell=new_link.cells[1],
    #                           value=new_link.candidate if type(first_link) is StrongLink else None,
    #                           invalidated_candidate=first_link.candidate if type(first_link) is WeakLink else None)
    #     if fictions[node].value == new_fiction.invalidated_candidate or fictions[node].invalidated_candidate == \
    #             new_fiction.value:
    #         return True
    #     else:
    #         return False


# def _find_sue_de_coq_in_intersection(board: Board,
#                                      block: Block,
#                                      crossing_house: House) -> Optional[Preview]:
#     intersection = block.get_unsolved_intersection_with_other_house(other_house=crossing_house)
#     if len(intersection) < 2:
#         return
#     cell_combinations = []
#
#     # do we have three non-solved cells with 5 distinct candidates?
#     if len(intersection) == 3 and len(board.get_distinct_candidates(cells=intersection)) == 5:
#         cell_combinations.append(intersection)
#
#     # # add each valid combination of two cells
#     # todo: unknown if it's allowed to choose any two out of three unsolved
#     # two_cell_combis_raw = tuple(itertools.combinations(intersection, 2))
#     # two_cell_combis = [c for c in two_cell_combis_raw if len(board.get_distinct_candidates(cells=c)) == 4]
#     # cell_combinations.extend(two_cell_combis)
#
#     for combination in cell_combinations:
#         intersection_candidates = set((c for cell in combination for c in cell.candidates))
#         assert (len(intersection_candidates) == 4 and len(combination) == 2) or (len(intersection_candidates) == 5
#                and len(combination) == 3)
#         # find bi-value cells in block and row/column
#         block.get_cells_having_only_candidates(candidates=intersection_candidates,
#                                                except_cells=combination)

#
# def find_empty_rectangle(board: Board):
#     """
#     if one candidate is restricted to one row and one column within a block, the remaining cells within form an ER.
#     we can then check for invalidations:
#         find a conjugate pair (a row or column containing only two candidates, one of them being our candidate) where
#         one of the candidates is in the row/col forming the ER.
#         If the col/row of the ER contains a candidate, that can see the second candidate of the conjugate pair,
#         it can be invalidated.
#     """
#
#     # find empty rectangles on the board
#     for block in board.get_all_houses(house_type=HouseType.BLOCK):
#         for candidate in block.candidates:
#             cells = block.get_cells_having_candidate(candidate=candidate)
#             if len(cells) < 3:
#                 continue
#             rows = [c.row for c in cells]
#             cols = [c.column for c in cells]
#             if len(set(rows)) != 2 or len(set(cols)) != 2:
#                 continue
#
#             # avoid squares; # todo unsure if an edge cell is a must, here it is
#             vertical_lines = set((col for col in cols if cols.count(col) > 1))
#             horizontal_lines = set((row for row in rows if rows.count(row) > 1))
#             if len(vertical_lines) != 1 or len(horizontal_lines) != 1:
#                 continue
#             horizontal_line, vertical_line = horizontal_lines.pop(), vertical_lines.pop()
#
#             class DirectionHorizontal(Enum):
#                 LEFT = 'left'
#                 RIGHT = 'right'
#
#             class DirectionVertical(Enum):
#                 TOP = 'top'
#                 BOTTOM = 'bottom'
#
#             @dataclass
#             class Direction:
#                 horizontal: DirectionHorizontal = None
#                 vertical: DirectionVertical = None
#
#             direction = Direction()
#             if [cell.y for cell in cells if cell.y > horizontal_line.y]:
#                 direction.vertical = DirectionVertical.BOTTOM
#             elif [cell.y for cell in cells if cell.y < horizontal_line.y]:
#                 assert not [cell.y for cell in cells if cell.y > horizontal_line.y]
#                 direction.vertical = DirectionVertical.TOP
#
#             # the empty rectangle to the left or right of a vertical line
#             if [cell.x for cell in cells if cell.x > vertical_line.x]:
#                 assert not [cell.x for cell in cells if cell.x < vertical_line.x]
#                 direction.horizontal = DirectionHorizontal.RIGHT
#             elif [cell.x for cell in cells if cell.x < vertical_line.x]:
#                 assert not [cell.x for cell in cells if cell.x > vertical_line.x]
#                 direction.horizontal = DirectionHorizontal.LEFT
#
#             # find a conjugate pair (a row or column containing only two candidates, one of them being our candidate)
#             # where one of the candidates is in the row/col forming the ER.
#             # If the col/row of the ER contains a candidate, that can see the second candidate of the conjugate pair,
#             # it can be invalidated.
#             cells_on_row_raw = horizontal_line.get_cells_having_candidate(candidate=candidate,
#                                                                           except_cells=cells)
#             if direction.horizontal is DirectionHorizontal.LEFT:
#                 cells_on_row = [c for c in cells_on_row_raw if c.x < vertical_line.x]
#             else:
#                 cells_on_row = [c for c in cells_on_row_raw if c.x > vertical_line.x]
#
#             cells_on_col_raw = vertical_line.get_cells_having_candidate(candidate=candidate,
#                                                                           except_cells=cells)
#             if direction.vertical is DirectionVertical.TOP:
#                 cells_on_col = [c for c in cells_on_col_raw if c.y < horizontal_line.y]
#             else:
#                 cells_on_col = [c for c in cells_on_col_raw if c.y > horizontal_line.y]
#
#             if not cells_on_row or not cells_on_col:
#                 continue
#
