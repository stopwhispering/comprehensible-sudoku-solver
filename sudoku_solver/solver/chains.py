from dataclasses import dataclass
from typing import List, Set, Tuple

from sudoku_solver.board.board import Board
from sudoku_solver.board.cell import Cell
from sudoku_solver.board.board_constants import LinkType
from sudoku_solver.board.preview import Preview, IndicatorLevel


@dataclass
class XChain(Preview):
    chain: List[Cell]
    candidate: int
    other_cells_seeing_start_and_end: Set[Cell]

    def get_preview_line_nodes(self) -> Tuple[Tuple[int, int, int]]:
        """create a line from chain start to chain end"""
        # just concatenate the x/y/c combination from start to end
        nodes = tuple((c.x, c.y, self.candidate) for c in self.chain)
        return nodes

    def get_invalidated_candidates(self) -> Tuple[Tuple[int, int, int]]:
        """return the board positions where the candidate is invalidated"""
        positions = tuple((c.x, c.y, self.candidate) for c in self.other_cells_seeing_start_and_end)
        return positions

    def execute(self):
        for cell in self.other_cells_seeing_start_and_end:
            cell.flag_candidates_invalid([self.candidate])


def extend_x_chain(board: Board, chain: List[Cell], candidate: int) -> XChain:
    """add another cell to an existing chain and check whether we can invalidate something
    if we can, return the cells where we can invalidate the candidate"""
    # get potential new chain elements
    previous_cell = chain[-1]
    required_link_type = LinkType.ANY if len(chain) % 2 == 0 else LinkType.STRONG
    linked_cells_raw = previous_cell.get_linked_cells(candidate=candidate, link_type=required_link_type)
    linked_cells = [c for c in linked_cells_raw if c not in chain]

    # create a chain version for each possible cell
    # if that new chain has an even number of cells, check if we can
    # use it to invalidate candidates for other cells
    for linked_cell in linked_cells:
        new_chain = chain.copy() + [linked_cell]

        if len(new_chain) % 2 == 0:
            # we can invalidate our candidate for all cells that see both starting and ending cell of the chain
            other_cells_seeing_start_and_end = board.get_cells_seeing_both_supplied_cells(candidate=candidate,
                                                                                          cell_a=new_chain[0],
                                                                                          cell_b=new_chain[-1])
            if other_cells_seeing_start_and_end:
                x_chain = XChain(chain=new_chain,
                                 candidate=candidate,
                                 other_cells_seeing_start_and_end=other_cells_seeing_start_and_end)
                return x_chain

        # extend chain once again
        cells_to_invalidate_candidate = extend_x_chain(board=board, chain=new_chain, candidate=candidate)
        return cells_to_invalidate_candidate


def find_x_chain(board: Board):
    """apply the x-chain logic
    - an x-chain has an even number of chained cells
    - odd links must be strong links, even links may be weak links (but can also be strong links)
    - either the starting or the ending cell has the candidate as it's value. therefore, all cells which are
        not part of the chain and which can see the both the starting and ending cell, may <<not>> have the
        candidate.
    """
    for candidate in range(1, 10):
        cells = board.get_cells_by_candidate(candidate=candidate)

        for starting_cell in cells:
            chain = [starting_cell]
            x_chain = extend_x_chain(board=board, chain=chain, candidate=candidate)
            if x_chain:
                # after finding a chain, we need to
                # return as all other chains may be inconsistent after invalidating
                # note: actual invalidating will happen as execute() fn of XChain object
                board.notify_preview(preview=x_chain)
                return


class XYChain(Preview):
    def __init__(self, starting_cell: Cell, starting_candidate: int):
        self.chain: List[ChainCell] = []
        self.other_cells: List[Cell] = []
        self.starting_candidate = starting_candidate
        self.add(starting_cell)

    def __contains__(self, cell: Cell):
        """override in operator"""
        return cell in [c.cell for c in self.chain]

    @property
    def last_cell(self) -> Cell:
        return self.chain[-1].cell

    @property
    def first_cell(self) -> Cell:
        return self.chain[0].cell

    @property
    def required_candidate_for_next_cell(self):
        if self.chain:
            return self.chain[-1].next_candidate
        else:
            return self.starting_candidate

    def add(self, cell):
        assert len(cell.possible_values) == 2
        assert self.required_candidate_for_next_cell in cell.possible_values
        next_candidate = [c for c in cell.possible_values if c != self.required_candidate_for_next_cell][0]
        self.chain.append(ChainCell(cell=cell,
                                    starting_candidate=self.required_candidate_for_next_cell,
                                    next_candidate=next_candidate))

    def pop(self) -> Cell:
        member = self.chain.pop()
        return member.cell

    def is_valid_xy_chain(self) -> bool:
        if len(self.chain) % 2 == 0 and self.chain[0].starting_candidate == self.chain[-1].next_candidate:
            return True
        else:
            return False

    def get_indicator_candidates(self) -> Tuple[Tuple[int, int, int, IndicatorLevel]]:
        positions = []
        first_start = (self.chain[0].cell.x, self.chain[0].cell.y, self.chain[0].starting_candidate,
                       IndicatorLevel.FIRST,)
        first_next = (self.chain[0].cell.x, self.chain[0].cell.y, self.chain[0].next_candidate,
                      IndicatorLevel.DEFAULT,)
        positions.append(first_start)
        positions.append(first_next)

        for member in self.chain:
            positions.append((member.cell.x, member.cell.y, member.starting_candidate, IndicatorLevel.DEFAULT))
            positions.append((member.cell.x, member.cell.y, member.next_candidate, IndicatorLevel.ALTERNATIVE))

        last_start = (self.chain[-1].cell.x, self.chain[-1].cell.y, self.chain[-1].starting_candidate,
                      IndicatorLevel.DEFAULT)
        last_next = (self.chain[-1].cell.x, self.chain[-1].cell.y, self.chain[-1].next_candidate,
                     IndicatorLevel.LAST)
        positions.append(last_start)
        positions.append(last_next)

        return tuple(positions)

    def get_invalidated_candidates(self) -> Tuple[Tuple[int, int, int]]:
        """return the board positions where the candidate is invalidated"""
        positions = tuple((c.x, c.y, self.starting_candidate) for c in self.other_cells)
        return positions

    def execute(self):
        for cell in self.other_cells:
            cell.flag_candidates_invalid([self.starting_candidate])


def _extend_xy_chain(board: Board, chain: XYChain) -> XYChain:
    """add (recursively) another cell to an existing xy chain and check whether we have a complete xy chain and
    can invalidate something"""
    linked_cells_raw = chain.last_cell.get_linked_cells(
            candidate=chain.required_candidate_for_next_cell,
            link_type=LinkType.ANY,
            n_candidates=2)
    linked_cells = [c for c in linked_cells_raw if c not in chain]

    # try out every possible way
    for linked_cell in linked_cells:
        # new_chain = copy(chain)
        chain.add(cell=linked_cell)

        # if chain...
        #   a) has an even number of cells (i.e. an odd number of links) and
        #   b) ends with the same candidate as it started,
        # then check if we can use it to invalidate candidates for other cells, otherwise go on
        if chain.is_valid_xy_chain():
            other_cells_seeing_start_and_end = board.get_cells_seeing_both_supplied_cells(
                    candidate=chain.starting_candidate,
                    cell_a=chain.first_cell,
                    cell_b=chain.last_cell)
            if other_cells_seeing_start_and_end:
                chain.other_cells = other_cells_seeing_start_and_end
                return chain

        xy_chain = _extend_xy_chain(board=board, chain=chain)
        if xy_chain:
            return xy_chain
        else:
            # remove last element
            chain.pop()


def find_xy_chain(board: Board):
    """todo"""
    for starting_candidate in range(1, 10):
        cells = board.get_cells_by_candidate(candidate=starting_candidate,
                                             n_candidates=2)
        for starting_cell in cells:
            chain = XYChain(starting_cell=starting_cell, starting_candidate=starting_candidate)

            xy_chain = _extend_xy_chain(board=board, chain=chain)
            if xy_chain:
                board.notify_preview(preview=xy_chain)
                return


@dataclass
class ChainCell:
    cell: Cell
    starting_candidate: int
    next_candidate: int