from enum import Enum


class FileType(Enum):
    IMAGE = 1
    CSV = 2


class BookLocation(Enum):
    LIBRARY = 'LIBRARY'
    LOAN = 'LOAN'
    CLASSROOM = 'CLASSROOM'


