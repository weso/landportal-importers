# coding=utf-8
__author__ = 'Dani'

from es.weso.util.excell_utils import is_empty_cell, is_empty_value, is_an_asterisc, is_numeric_value, \
    is_an_special_under_five_value
from es.weso.translator.parser.parsed_entities import ParsedCountry, ParsedValue


class CountriesParser(object):
    def __init__(self, sheet):
        self.sheet = sheet
        self.first_row = None
        self.last_row = None
        self.countries = []

    def run(self):
        self.first_row = self._look_for_first_countries_row()
        self.last_row = self._look_for_last_countries_row()
        self.parse_countries()
        # for country in self.countries:
        #     print country.name
        #     print "Nº of values:", len(country.values)
        return self.countries


    def parse_countries(self):
        for i in range(self.first_row, self.last_row + 1):
            country_row = self.sheet.row(i)
            new_country = ParsedCountry()
            new_country.name = self._parse_country_name(country_row)
            new_country.values = self._parse_country_values(country_row)
            self.countries.append(new_country)
        pass


    def _parse_country_name(self, country_row):
        if is_empty_cell(country_row[0]):
            raise RuntimeError("Unable to detect name country in row {0}.".format(country_row))
        return country_row[0].value.encode('utf-8')

    def _parse_country_values(self, country_row):
        values = []
        cell_cursor = 1
        current_value = None

        while cell_cursor < self.sheet.ncols:
            cell_value = country_row[cell_cursor].value

            if is_an_asterisc(cell_value):
                current_value.estimated = False  # It must be here a ParsedValue
            elif is_empty_value(cell_value):
                pass  # Nothing to do... but it is an acceptable case
            elif is_an_special_under_five_value(cell_value):
                current_value = ParsedValue()
                current_value.column = cell_cursor
                current_value.estimated = False
                current_value.value = 0  # Sure about this?????
                current_value.estimated = True
                values.append(current_value)
            elif is_numeric_value(cell_value):
                current_value = ParsedValue()
                current_value.column = cell_cursor
                current_value.estimated = False
                current_value.value = float(cell_value)
                values.append(current_value)
            else:
                print cell_value
                raise RuntimeError("Unexpected content in country cell")
            cell_cursor += 1

        return values


    def _look_for_first_countries_row(self):
        """
        We sould look for the next row after the fist that has 'country'
        as content in it first column

        """
        for i in range(0, self.sheet.nrows):
            candidate_row = self.sheet.row(i)
            if candidate_row[0].value == "Country" and i < self.sheet.nrows - 1:
                return i + 1  # Next to the one that contains "Country"

        raise RuntimeError('Unable to locate countries in excell. Provided file does not follow expected conventions')

    def _look_for_last_countries_row(self):
        """
        Once we start countries, we will look for the first empty row. Our row
        will be the one that preceed that. If we do not find an empty row, the the final
        one should be the last of the file


        """
        for i in range(self.first_row, self.sheet.nrows):
            candidate_row = self.sheet.row(i)
            if is_empty_cell(candidate_row[0]):
                return i - 1  # The one that preceed the first empty

        return self.sheet.nrows - 1  # The last of the file if we could not find any empty

