__author__ = 'Dani'


class ParsedIndicator(object):

    def __init__(self, name=None, beg_column=None, end_column=None):
        self.name = name
        self.beg_col = beg_column
        self.end_col = end_column


class ParsedDate(object):
    def __init__(self, string_date=None, beg_column=None, end_column=None):
        self.string_date = string_date
        self.beg_col = beg_column
        self.end_col = end_column


class ParsedCountry(object):
    def __init__(self, name=None):
        self.name = name
        self.values = []


class ParsedValue(object):
    def __init__(self, value=None, column=None, estimated=False):
        self. value = value
        self.column = column
        self.estimated = estimated
