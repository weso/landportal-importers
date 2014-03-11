__author__ = 'Dani'

from es.weso.util.excell_utils import is_empty_cell, content_starts_in_second_column
from es.weso.translator.parser.parsed_entities import ParsedIndicator


class IndicatorsParser(object):

    def __init__(self, sheet):
        self.sheet = sheet
        self.row = None  # Complete when running
        self.indicators = []  # Complete when running

    def run(self):
        self.row = self._look_for_indicators_row()
        self.parse_indicators()
        # for indicator in self.indicators:
        #     print indicator.name, indicator.beg_col, indicator.end_col
        return self.indicators



    def parse_indicators(self):
        #Looking for first available content
        cursor = 0 #cursor will be used as a pointer to cells in a row
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
            new_indicator = self._build_parsed_indicator(index_begin, cursor - 1)
            index_begin = cursor
            cursor += 1
            self.indicators.append(new_indicator)



    def _build_parsed_indicator(self, index_beg, index_end):
        new_indicator = ParsedIndicator()
        new_indicator.name = self.row[index_beg].value.encode("utf-8")
        new_indicator.beg_col = index_beg
        new_indicator.end_col = index_end
        return new_indicator

    def _look_for_indicators_row(self):
        """
        It looks like the indicator row is the first one with data in the second col.
        It makes sense, because, as main header, should be over date and, for sure,
        over concrete data observations. It also makes sense to start in the second
        col, not in the first, because first is reserved to country_names.
        We should trust in that theory to locate the indicators row.

        """
        for i in range(0, self.sheet.nrows):
            candidate_row = self.sheet.row(i)
            if content_starts_in_second_column(candidate_row):
                return candidate_row

        raise RuntimeError("No indicators row found. Impossible to parse file")




