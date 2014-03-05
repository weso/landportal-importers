__author__ = 'Dani'

from .parser.parser import Parser
from .model_object_builder import IpfriModelObjectBuilder
import xlrd


class IpfriTranslator(object):

    def __init__(self, file_path):
        self.file_path = file_path
        self.sheet = None

    def run(self):
        self.sheet = self.take_data_sheet_from_file_path()
        indicators, dates, countries = Parser(self.sheet).run()
        IpfriModelObjectBuilder(indicators, dates, countries).run()


    def take_data_sheet_from_file_path(self):
        book = xlrd.open_workbook(self.file_path)
        #We are assuming that the sheet with the data is placed the last in the book
        return book.sheet_by_index(book.nsheets - 1)


