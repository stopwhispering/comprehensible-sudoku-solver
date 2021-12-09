from typing import List

from sudoku_solver.board.board import Board
from sudoku_solver.board.cell import Cell
from sudoku_solver.board.board_constants import LinkType
from sudoku_solver.solver.artefacts import XYChain, XChain


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


