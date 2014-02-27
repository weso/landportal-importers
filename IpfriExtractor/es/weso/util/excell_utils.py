__author__ = 'Dani'


def is_empty_cell(cell):
    if cell.value in [None, "", " "]:
        return True
    return False