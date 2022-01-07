import itertools
from dataclasses import dataclass
from typing import Sequence, Set, List, Tuple

from sudoku_solver.board.board import Board
from sudoku_solver.board.cell import Cell
from sudoku_solver.shared.preview import Preview, IndicatorLevel, HighlightedPosition
from sudoku_solver.shared.puzzle import ValuePosition
from sudoku_solver.solver.decorators import evaluate_algorithm


@dataclass
class RemotePairMember:
    cell: Cell
    type: str  # 'odd' or 'even'
    other_cells: Set[Cell]


class RemotePair(Preview):
    def __init__(self, candidates: Sequence[int]):
        self.candidates = candidates
        self.members: List[RemotePairMember] = []
        self.other_cells_to_invalidate: Set = set()

    def __contains__(self, cell: Cell):
        """override <<in>> operator"""
        member_cells = [member.cell for member in self.members]
        return cell in member_cells

    def _other_cell_sees_member_type(self, other_cell: Cell, type_: str):
        """check whether a cell sees an 'odd' or 'even' member cell"""

    def determine_cells_to_invalidate(self):
        """among all other cells, we identify those that see both an odd member cell
        and an even member cell"""
        seeing_odd_members: List[Cell] = []
        seeing_even_members: List[Cell] = []
        for member in [member for member in self.members if member.type == 'odd']:
            seeing_odd_members.extend(member.other_cells)
        for member in [member for member in self.members if member.type == 'even']:
            seeing_even_members.extend(member.other_cells)
        self.other_cells_to_invalidate = set(seeing_odd_members).intersection(set(seeing_even_members))

    def execute(self) -> None:
        """execute the invalidation of candidates"""
        for cell in self.other_cells_to_invalidate:
            cell.flag_candidates_invalid(self.candidates)

    def get_invalidated_candidates(self) -> Sequence[ValuePosition]:
        """get the candidate positions to be invalidated"""
        invalidated = []
        for cell in self.other_cells_to_invalidate:
            invalidated.extend([ValuePosition(x=cell.x, y=cell.y, value=candidate) for candidate in cell.candidates
                                if candidate in self.candidates])
        return invalidated

    def get_indicator_candidates(self) -> Sequence[HighlightedPosition]:
        """get candidate positions to be highlighted"""
        positions = []
        for member in [member for member in self.members if member.type == 'odd']:
            positions.extend([HighlightedPosition(x=member.cell.x,
                                                  y=member.cell.y,
                                                  value=candidate,
                                                  indicator_level=IndicatorLevel.DEFAULT,
                                                  ) for candidate in member.cell.candidates])

        for member in [member for member in self.members if member.type == 'even']:
            positions.extend([HighlightedPosition(x=member.cell.x,
                                                  y=member.cell.y,
                                                  value=candidate,
                                                  indicator_level=IndicatorLevel.ALTERNATIVE,
                                                  ) for candidate in member.cell.candidates])

        return positions


def _is_remote_pair(cells: Sequence[Cell]):
    assert len(set([tuple(c.candidates) for c in cells])) == 1
    assert len(cells) >= 4
    for i in range(1, len(cells)):
        if not cells[i].is_seen_by_cell(other_cell=cells[i - 1]):
            return False
    return True


def _find_remote_pairs_for_candidate_combination(candidates: Sequence[int],
                                                 combi_cells: List[Cell]) -> List[Tuple[RemotePair, int]]:
    # build the longest possible chain by testing all cell orders (and all lengths 4+)
    assert len(combi_cells) >= 4
    remote_pairs: List[Tuple[RemotePair, int]] = []

    cell_combinations = []
    for length in range(4, len(combi_cells) + 1):
        cell_combinations.extend(list(itertools.permutations(combi_cells, length)))

    cell_combination: Tuple[Cell]
    for cell_combination in cell_combinations:
        if _is_remote_pair(cells=cell_combination):

            # to identify candidates in other cells to invalidate,
            # we first collect the relevant external cells seeing each cell in the remote pair
            remote_pair = RemotePair(candidates=candidates)
            for i, cell in enumerate(cell_combination):
                other_cells = cell.seen_by_any_of_candidates(candidates=candidates)
                member = RemotePairMember(cell=cell,
                                          type='odd' if i % 2 == 1 else 'even',
                                          other_cells=other_cells)
                remote_pair.members.append(member)
            remote_pair.determine_cells_to_invalidate()
            count_to_invalidate = len(remote_pair.other_cells_to_invalidate)
            if count_to_invalidate:
                remote_pairs.append((remote_pair, count_to_invalidate))
    return remote_pairs


@evaluate_algorithm
def find_remote_pair(board: Board):
    """we need a chain of 4+ cells each with the same (exactly) two candidates; consider each of these cells
    to have an odd number or an even number; we may then invalidate the two candidates from each other (i.e.
    external) cell that sees both an odd and an even remote pair cell.
    often, a longer chain enables invalidating more candidates than a shorter chain"""
    # identify all candidate combinations of two with 4+ cells
    twin_cells = board.get_cells_by_number_of_candidates(n_candidates=2)
    combinations = [tuple(c.candidates) for c in twin_cells]
    combinations_min_four = [combi for combi in combinations if combinations.count(combi) >= 4]
    distinct_combinations_min_four = set(combinations_min_four)
    for candidate_combination in distinct_combinations_min_four:
        combi_cells = [c for c in twin_cells if tuple(c.candidates) == candidate_combination]

        # find remote pairs for current combination of two candidates (and their cells)
        remote_pairs = _find_remote_pairs_for_candidate_combination(candidates=candidate_combination,
                                                                    combi_cells=combi_cells)
        if remote_pairs:
            # apply remote pair that invalidates the most other cells' candidates
            remote_pairs_sorted_desc = sorted(remote_pairs, key=lambda r: r[1], reverse=True)
            remote_pair_max_invalidations = remote_pairs_sorted_desc[0]
            board.notify_preview(preview=remote_pair_max_invalidations[0])
            return
