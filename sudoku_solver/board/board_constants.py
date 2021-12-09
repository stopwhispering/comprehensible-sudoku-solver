from enum import Enum

HORIZONTAL_INDEXES = list(range(9))
VERTICAL_INDEXES = list(range(9))


class LinkType(Enum):
    WEAK = 1
    STRONG = 2
    ANY = 3