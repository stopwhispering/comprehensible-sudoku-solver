from typing import List, Union, Tuple

from sudoku_solver.board.cell import Cell
from sudoku_solver.shared.preview import PreviewArrow, IndicatorLevel, HighlightedPosition
from sudoku_solver.shared.puzzle import ValuePosition
from sudoku_solver.util.exceptions import ChainError
from sudoku_solver.solver.common.links import Link, StrongLink, WeakLink


class Chain:
    links: List[Link]

    def __init__(self):
        self.links = []

    def __len__(self):
        return len(self.links)

    def __repr__(self):
        info = ''
        for i, link in enumerate(self.links):
            op = '=' if isinstance(link, StrongLink) else '-'
            joined_cell = f'[R{link.cells[1].y}C{link.cells[1].x}]'
            if i == 0:
                starting_cell = f'[R{link.cells[0].y}C{link.cells[0].x}]'
                info += f'{starting_cell}{op}{link.candidate}{op}{joined_cell}'
            else:
                info += f'{op}{link.candidate}{op}{joined_cell}'
        return info

    def __contains__(self, item: Union[Cell, Link]):
        if isinstance(item, Link):
            return item in self.links
        elif isinstance(item, Cell):
            return item in self.cells
        else:
            raise TypeError

    @property
    def cells(self) -> List[Cell]:
        return [cell for link in self.links for cell in link.cells]

    @property
    def empty(self):
        return not self.links

    @property
    def starting_cell(self):
        assert self.links and self.links[0].cells
        return self.links[0].cells[0]

    def add_link(self, link: Link):
        assert isinstance(link, Link)
        self.links.append(link)

    def pop_link(self):
        return self.links.pop()

    def get_arrows_for_preview(self) -> List[PreviewArrow]:
        assert self.links[-1].cells[1] is self.links[0].cells[0]
        arrows = []
        # generate an arrow for each link
        for link in self.links:
            pos_from = ValuePosition(x=link.cells[0].x, y=link.cells[0].y, value=link.candidate)
            pos_to = ValuePosition(x=link.cells[1].x, y=link.cells[1].y, value=link.candidate)
            indicator_level = IndicatorLevel.DEFAULT if isinstance(link, WeakLink) else IndicatorLevel.ALTERNATIVE
            arrows.append(PreviewArrow(pos_from=pos_from, pos_to=pos_to, indicator_level=indicator_level))
        return arrows

    def get_indicators_for_preview(self) -> Tuple[HighlightedPosition]:
        assert self.links[-1].cells[1] is self.links[0].cells[0]
        indicators = []
        for i, link in enumerate(self.links):
            cell_a, cell_b = link.cells
            if i == 0:
                indicators.append(HighlightedPosition(cell_a.x, cell_a.y, link.candidate, IndicatorLevel.FIRST))
            else:
                indicators.append(HighlightedPosition(cell_a.x, cell_a.y, link.candidate, IndicatorLevel.DEFAULT))
            if i == len(self.links) - 1:
                indicators.append(HighlightedPosition(cell_b.x, cell_b.y, link.candidate, IndicatorLevel.LAST))
            else:
                indicators.append(HighlightedPosition(cell_b.x, cell_b.y, link.candidate, IndicatorLevel.DEFAULT))

        return tuple(indicators)

    def get_invalidations_for_discontinuous_nice_loop(self) -> Tuple[Tuple[Cell, int]]:
        # check if the last link and the final link (with the first cell as the node inbetween) fulfill the
        # conditions for a discontinuous nice loop
        assert self.links[0].cells[0] is self.links[-1].cells[1]
        node = self.links[0].cells[0]
        link_last, link_first = self.links[-1], self.links[0]
        candidate_last, candidate_first = link_last.candidate, link_first.candidate
        link_types = (type(link_last), type(link_first))

        # I - if the first cell has two weak links for the same candidate, that candidate can be invalidated
        if (isinstance(link_last, WeakLink) and isinstance(link_first, WeakLink)) and candidate_last == \
                candidate_first:
            print(f'Discontinuous Nice Loop (Type I): {self} => {repr(node)} not {candidate_first}')
            return (node, candidate_first),

        # II - if the first cell has two strong links for the same candidate, then we can consider the candidate true
        if (isinstance(link_last, StrongLink) and isinstance(link_first, StrongLink)) and candidate_last == \
                candidate_first:
            print(f'Discontinuous Nice Loop (Type II): {self} => {repr(node)} is <<{candidate_first}>>')
            invalid_candidates = [c for c in node.candidates if c != candidate_first]
            return tuple((node, c) for c in invalid_candidates)

        # III - if the first cell has a weak and a strong link with different candidates, then the weak link's
        # candidate can be invalidated
        if StrongLink in link_types and WeakLink in link_types and candidate_last != candidate_first:
            invalid_candidate = link_first.candidate if isinstance(link_first, WeakLink) else link_last.candidate
            print(f'Discontinuous Nice Loop (Type III): {self} => {repr(node)} not {invalid_candidate}')
            return (node, invalid_candidate),

        return tuple()

    def is_valid_next_link(self, link: Link):
        if not self.links:
            return True
        assert self.links[-1].cells[1] is link.cells[0]
        assert self.links[-1].cells[1].has_candidate(link.candidate)
        node = link.cells[0]
        link_in, link_out = self.links[-1], link

        # If a node has two Strong links, the digits must be different
        if isinstance(link_in, StrongLink) and isinstance(link_out, StrongLink):
            assert node.has_candidate(link_in.candidate) and node.has_candidate(link_out.candidate)
            return link_in.candidate != link_out.candidate

        # If a node has two weak links, the cell must be two-valued and the digits must be different
        elif isinstance(link_in, WeakLink) and isinstance(link_out, WeakLink):
            return node.count_candidates == 2 and link_in.candidate != link_out.candidate

        # If a node has two different links (one weak, one strong), the digits must be the same
        elif type(link_in) in (StrongLink, WeakLink) and type(link_out) in (StrongLink, WeakLink):
            return link_in.candidate == link_out.candidate

        else:
            raise ChainError('Unknown Link Type')