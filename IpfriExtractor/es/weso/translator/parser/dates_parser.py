__author__ = 'Dani'

from es.weso.util.excell_utils import is_empty_cell, content_starts_in_second_column
from es.weso.translator.parser.parsed_entities import ParsedDate

class DatesParser(object):

    def __init__(self, sheet):
        self.sheet = sheet
        self.row = None
        self.dates = []

    def run(self):
        self.row = self._look_for_dates_row()
        self._parse_dates()
        # for date in self.dates:
        #     print date.string_date, date.beg_col, date.end_col
        return self.dates

    def _parse_dates(self):
        #Looking for first available content
        cursor = 0  # cursor will be used as a pointer to cells in a row
        while is_empty_cell(self.row[cursor]):
            cursor += 1
        #When we find content, we save it index in index_begin (current cursor value)
        index_begin = cursor
        cursor += 1
        while cursor <= self.sheet.ncols:
            while cursor < self.sheet.ncols and is_empty_cell(self.row[cursor]): #When we find a non empty cell, we have
                                                                #reach a new indicator. We have to save the old one. In
                                                                #the case of the last indicator, we will not find a non
                                                                #empty cell, but the end of the cells. That is why we
                                                                #are using the first part of the condition
                cursor += 1
            new_date = self._build_parsed_date(index_begin, cursor - 1)
            index_begin = cursor
            cursor += 1
            self.dates.append(new_date)

    def _look_for_dates_row(self):
        """
        We should look for the second row with content starting in the second
        col. The first row that starts with content in the second col is the
        indicators one

        """
        appropiate_rows_counter = 0
        for i in range(0, self.sheet.nrows):
            candidate_row = self.sheet.row(i)
            if content_starts_in_second_column(candidate_row):
                appropiate_rows_counter += 1
                if appropiate_rows_counter == 2:
                    return candidate_row

        raise RuntimeError("No dates row found. Impoissible to parse file")


    def _build_parsed_date(self, index_begin, index_end):
        new_date = ParsedDate()
        new_date.beg_col = index_begin
        new_date.end_col = index_end
        new_date.string_date = self.row[index_begin].value
        return new_date


