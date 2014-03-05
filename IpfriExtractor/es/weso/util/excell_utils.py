__author__ = 'Dani'


def is_empty_cell(cell):
    if cell.value in [None, "", " "]:
        return True
    return False


def is_empty_value(value):
    if value in [None, "", " "]:
        return True
    return False


def content_starts_in_second_column(candidate_row):
    #First col should be empty
    if not is_empty_cell(candidate_row[0]):
        return False
    #Second column should have content
    if is_empty_cell(candidate_row[1]):
        return False
    return True

def is_an_asterisc(value):
    if value == "*":
        return True
    return False


def is_numeric_value(value):
    try:
        float(value)
        return True
    except:
        return False


def is_an_special_under_five_value(value):
    if value == "<5":
        return True
    return False