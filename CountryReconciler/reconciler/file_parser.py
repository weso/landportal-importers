"""
Created on 10/02/2014

@author: Dani
"""

import ConfigParser

import xlrd

from reconciler.entities.parsed_country import ParsedCountry
from reconciler.exceptions.parsing_error import ParsingError
from reconciler.exceptions.unknown_country_error import UnknownCountryError

import os.path


class FileParser(object):
    """
    The utility of this class is, as its name says, to parse the Excel file from which
    we'll normalize the countries passed by the data sources' importers. In order to
    carry out this task, it will load the file from the path specified in configuration.ini
    and will parse the range of rows determined by FIRST_ROW and LAST_ROW attributes. If
    new countries are added or removed from the file, we'll have to modify these attributes.

    Also, if we find a data source that identifies the countries in any other way than ISO3,
    ISO2, UN code, FAOSTAT code or country name, it will be necessary to parse this identifier
    from the Excel file.
    """

    #ROW INDEX
    FIRST_ROW = 1
    LAST_ROW = 248

    #COLUMN INDEX
    ISO3_FAO_COL = 4
    ISO3_OFFICIAL_COL = 3
    ISO3_A2_COL = 28
    ISO2_COL = 27
    UN_OFFICIAL_CODE_COL = 29
    FAOSTAT_CODE_COL = 47

    SNAME_EN_FAO_COL = 6
    SNAME_ES_FAO_COL = 8
    SNAME_FR_FAO_COL = 10

    LNAME_EN_FAO_COL = 5
    LNAME_ES_FAO_COL = 7
    LNAME_FR_FAO_COL = 9

    ALT_EN_NAME_1_COL = 2
    ALT_EN_NAME_2_COL = 11



    def __init__(self):
        # self.config = ConfigParser.ConfigParser()
        # # self.config.read('../conf/configuration.ini')
        # self.config.read('C:/Users/Dani/Documents/EII/WESO/wesopace/CountryReconciler/reconciler/conf/configuration.ini')
        self.country_list = []

    def run(self):
        # countries_source_file = self.config.get('SOURCE', 'path_file_countries')
        countries_source_file = os.path.dirname(__file__) + "/files/country_list.xlsx" # Without config, but works better
        self.parse_countries(countries_source_file)
        # alias_file = self.config.get('SOURCE', 'path_file_alias')
        alias_file = os.path.dirname(__file__) + "/files/known_alias.txt"  # Without config, but works better
        self.parse_alias(alias_file)
        return self.country_list

    def parse_alias(self, alias_file):
        alias_file_content = open(alias_file)
        lines = alias_file_content.readlines()
        for a_line in lines:
            self._process_alias_line(a_line)
        alias_file_content.close()
        pass

    def _process_alias_line(self, a_line):
        line_parts = a_line.split("=")
        if not len(line_parts) == 2:
            return #We have found a white line. Just ignore it
        target_country = self.get_country_by_iso3(line_parts[0])
        target_country.add_alias(line_parts[1])

        pass

    def get_country_by_iso3(self, iso3):
        for a_country in self.country_list:
            if a_country.get_iso3() == iso3:
                return a_country
        #We reach the next sentence if we could not find a coincidence with the iso3
        raise UnknownCountryError("Trying to add a alias to a non recognized country: {0}".format(iso3))
        # print "Trying to add a alias to a non recognized country: {0}".format(iso3)

    def parse_countries(self, path):
        book = xlrd.open_workbook(path, encoding_override='latin-1').sheet_by_index(0)
        self.parse_row_range(book, self.FIRST_ROW, self.LAST_ROW)

    def parse_row_range(self, book, first, last):
        for row in range(first, last + 1):
            iso3_official = self.parse_iso(book, row, self.ISO3_OFFICIAL_COL)
            iso3_fao = self.parse_iso(book, row, self.ISO3_FAO_COL)
            iso3_a2 = self.parse_iso(book, row, self.ISO3_A2_COL)
            iso2 = self.parse_iso(book, row, self.ISO2_COL)

            sname_en = self.parse_name(book, row, self.SNAME_EN_FAO_COL)
            sname_es = self.parse_name(book, row, self.SNAME_ES_FAO_COL)
            sname_fr = self.parse_name(book, row, self.SNAME_FR_FAO_COL)

            un_code = self.parse_numeric_code(book, row, self.UN_OFFICIAL_CODE_COL)
            faostat_code = self.parse_numeric_code(book, row, self.FAOSTAT_CODE_COL)

            lname_en = self.parse_name(book, row, self.LNAME_EN_FAO_COL)
            lname_es = self.parse_name(book, row, self.LNAME_ES_FAO_COL)
            lname_fr = self.parse_name(book, row, self.LNAME_FR_FAO_COL)

            alt_en_name1 = self.parse_name(book, row, self.ALT_EN_NAME_1_COL)
            alt_en_name2 = self.parse_name(book, row, self.ALT_EN_NAME_2_COL)

            country = ParsedCountry(iso3_official,
                                    iso3_fao,
                                    iso3_a2,
                                    iso2,
                                    sname_en,
                                    sname_es,
                                    sname_fr,
                                    un_code,
                                    faostat_code,
                                    lname_en,
                                    lname_es,
                                    lname_fr,
                                    alt_en_name1,
                                    alt_en_name2
                                    )
            if country.get_iso3() is not None:
                self.country_list.append(country)

                # ---Dirty debugging stuff---
                # print country.get_iso3()
                # if country.iso2 is not None:
                #     print '\t' + country.iso2
                # if country.un_code is not None:
                #     print '\t' + str(country.un_code)
                # if country.sname_en is not None:
                #     print "\t" + country.sname_en

            else:
                raise ParsingError('File malformed. There are country rows with no ISO3 code')

    def parse_iso(self, book, row, col):
        value = book.row(row)[col].value
        if self.is_white_value(value) or value == '-99' or value == -99:
            # Invalid ISO2 codes in the Excel file are marked as '-99',
            # some stored as text, and some as numeric value
            return None
        return str(value)

    def parse_name(self, book, row, col):
        value = unicode(book.row(row)[col].value)
        if self.is_white_value(value):
            return None
        return value.encode(encoding="utf-8")

    def parse_numeric_code(self, book, row, col):
        value = book.row(row)[col].value
        if self.is_white_value(value) or int(value) == -99:
            return None
        return int(value)

    @staticmethod
    def is_white_value(value):
        if value is None or value == "":
            return True
        return False