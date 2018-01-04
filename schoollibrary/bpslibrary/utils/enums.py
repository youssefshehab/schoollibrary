"""Module to contain all enums in the system."""


from enum import Enum


class FileType(Enum):
    """Types of files handled in the system."""

    IMAGE = 1
    CSV = 2


class BookLocation(Enum):
    """Locations of books."""

    LIBRARY = 'LIBRARY'
    LOAN = 'LOAN'
    CLASSROOM = 'CLASSROOM'
