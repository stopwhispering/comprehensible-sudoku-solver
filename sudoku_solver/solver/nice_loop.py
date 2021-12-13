from typing import Optional

from sudoku_solver.board.board import Board
from sudoku_solver.board.cell import Cell
from sudoku_solver.board.preview import CommonPreview
from sudoku_solver.solver.common.chains import Chain
from sudoku_solver.solver.common.links import create_link
from sudoku_solver.solver.solver_constants import NICE_LOOP_MAX_LINKS


def _extend_chain_to_loop(cell_in: Cell, chain: Chain) -> Optional[CommonPreview]:
    # if our chain has already reached max size (to keep computation fast and to keep the strategy humanly
    # comprehensible), we will only try to link back to the starting cell
    seen_cells = [chain.starting_cell] if not chain.empty and cell_in.is_seen_by_cell(chain.starting_cell) else []
    if len(chain) >= NICE_LOOP_MAX_LINKS:
        if not seen_cells:
            return
    else:
        # with any seen cell/candidate, out cell_in can at least form a weak link
        # note: a cell may be in the chain only once with the exception of the starting cell
        seen_cells.extend(cell_in.seen_by_any_of_candidates(candidates=cell_in.candidates,
                                                            except_cells=chain.cells))

    for cell_out in seen_cells:
        # each seen cell might have multiple candidates we could form a link with
        for candidate in set(cell_in.candidates).intersection(cell_out.candidates):
            link = create_link(candidate, cell_in=cell_in, cell_out=cell_out)
            if not chain.is_valid_next_link(link):
                continue

            # if we're back at the starting cell (i.e. have finished the loop), we determine whether
            # we have a discontinuous or continuous nice loop
            # in both cases, we may likely invalidate some candidate(s)
            if not chain.empty and cell_out is chain.starting_cell:
                # todo <<continuous>> nice loop (very rare)

                chain.add_link(link)
                # discontinuous nice loop
                invalidated_cells = chain.get_invalidations_for_discontinuous_nice_loop()
                if not invalidated_cells:
                    chain.pop_link()
                    continue

                return CommonPreview(invalidated_cells=invalidated_cells,
                                     indicator_candidates=chain.get_indicators_for_preview(),
                                     indicator_arrows=chain.get_arrows_for_preview())

            # extend the chain by finding another link
            # (we set a limit to the number of links to keep the strategy humanly comprehensible)
            elif len(chain) <= NICE_LOOP_MAX_LINKS:
                chain.add_link(link)

                # find another node
                preview = _extend_chain_to_loop(cell_in=cell_out, chain=chain)
                if preview:
                    return preview
                else:
                    chain.pop_link()


def find_nice_loop(board: Board):
    """Nice Loop Strategy, currently only <<discontinuous>> version implemented"""
    # start with <<any>> unsolved cell
    chain = Chain()
    cells = board.get_cells(only_unsolved=True)
    for cell in cells:
        preview = _extend_chain_to_loop(cell_in=cell, chain=chain)
        if preview:
            board.notify_preview(preview=preview)
            return
