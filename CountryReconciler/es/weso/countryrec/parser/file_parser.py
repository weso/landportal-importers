"""
Created on 10/02/2014

@author: Dani
"""

import xlrd
import ConfigParser
import logging

from es.weso.countryrec.entities.parsed_country import ParsedCountry
from es.weso.countryrec.normalizer.country_normalizer import CountryNormalizer


class FileParser(object):
    #ROW INDEX
    FIRST_ROW = 1
    LAST_ROW = 247

    #COLUMN INDEX
    ISO2_COL = 22
    ISO3_FAO_COL = 4
    ISO3_OFFICIAL_COL = 3
    NAME_FAO_COL = 5
    NAME_OFFICIAL_COL = 2
    UN_ALT_CODE = 24
    UN_OFFICIAL_CODE = 25

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read('../conf/configuration.ini')
        self.configure_log()
        self.log = logging.getLogger('es.weso.countryrec.parser.file_parser')
        self.source_file = self.config.get('SOURCE', 'path_file')
        self.country_list = []  # Will contain all the country objects

    def configure_log(self):
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(filename='countryrec.log', level=logging.WARNING,
                        format=log_format)

    def run(self):
        self.parse_file()
        return self.country_list

    def parse_file(self):
        book = xlrd.open_workbook(self.source_file).sheet_by_index(0)
        self.parse_row_range(book, self.FIRST_ROW, self.LAST_ROW)

    def parse_row_range(self, book, first, last):
        for row in range(first, last + 1):
            row_in_file = row
            iso3_official = self.parse_iso(book, row, self.ISO3_OFFICIAL_COL)
            iso3_fao = self.parse_iso(book, row, self.ISO3_FAO_COL)
            name_fao = self.parse_name(book, row, self.NAME_FAO_COL)
            name_official = self.parse_name(book, row, self.NAME_OFFICIAL_COL)
            un_code = self.parse_code(book, row, self.UN_OFFICIAL_CODE)
            un_opt_code = self.parse_code(book, row, self.UN_ALT_CODE)
            country = ParsedCountry(row_in_file, iso3_official, iso3_fao,
                                    name_official, name_fao, un_code, un_opt_code)
            self.country_list.append(country)

    def parse_iso(self, book, row, col):
        value = book.row(row)[col].value
        if self.white_value(value):
            self.log.warning('Blank iso value in row ' + str(row) + ', col ' + str(col))
            return None
        return str(value).strip()

    def parse_name(self, book, row, col):
        value = unicode(book.row(row)[col].value)
        if self.white_value(value):
            self.log.warning('Blank name value in row ' + str(row) + ', col ' + str(col))
            return None
        return value

    def parse_code(self, book, row, col):
        value = book.row(row)[col].value
        if self.white_value(value):
            self.log.warning('Blank un code value in row ' + str(row) + ', col ' + str(col))
            return None
        elif int(value) < 0:
            self.log.warning('Invalid un code value in row ' + str(row) + ', col ' + str(col))
            return None
        return int(value)

    @staticmethod
    def white_value(value):
        if value is None or value == "":
            return True
        return False