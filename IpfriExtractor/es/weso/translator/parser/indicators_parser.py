__author__ = 'Dani'

from es.weso.util.excell_utils import is_empty_cell
from es.weso.translator.parser.parsed_entities import ParsedIndicator


class IndocatorsParser(object):

    def __init__(self, sheet):
        self.sheet = sheet
        self.row = None  # Complete when running
        self.indicators = []  # Complete when running

    def run(self):
        self.row = self._look_for_indicators_row()
        self.parse_indicators()


    def parse_indicators(self):
        #Looking for first available content
        index_beg = 0
        index_end = 0
        cursor = 0
        while is_empty_cell(self.row[cursor]):
            cursor += 1
        #Loop broken when we find some content
        index_begin = cursor
        cursor += 1
        while cursor < self.sheet.nrows:  # Bad idea
            while is_empty_cell(self.row[cursor]):
                cursor += 1
            new_indicator = self.build_parsed_indicator(index_beg, cursor - 1)
            # TODO : COMPLETE THE ALGORITH TO STORE THE INDICATORS

        pass


    def build_parsed_indicator(self, index_beg, index_end):
        new_indicator = ParsedIndicator()
        new_indicator.name = self.row[index_beg].value
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
            candidate_row = self.sheet.row[i]
            if self._content_starts_in_second_column(candidate_row):
                return candidate_row

        raise RuntimeError("No indicators row found. Impossible to parse file")

    @staticmethod
    def _content_starts_in_second_column(candidate_row):
        #First col should be empty
        if not is_empty_cell(candidate_row[0]):
            return False
        #Second column should have content
        if is_empty_cell(candidate_row[1]):
            return False
        return True



