__author__ = 'Dani'

import xlrd

from model2xml.model2xml import ModelToXMLTransformer
from .parser.parser import Parser
from .object_builder.model_object_builder import IpfriModelObjectBuilder

from datetime import datetime
import os.path


class IpfriTranslator(object):

    def __init__(self, log, config, look_for_historical=True):
        self.paths_to_files = []
        self.log = log
        self.config = config
        self.look_for_historical = look_for_historical
        self.dataset_user_pairs = []

    def run(self):
        self.determine_paths_to_files()
        self.translate_files_into_model_objects()
        self.translate_model_objects_into_xml()



    def translate_files_into_model_objects(self):
        i = 0
        for a_path in self.paths_to_files:
            i += 1
            a_sheet = self.take_data_sheet_from_file_path(a_path)
            indicators, dates, countries = Parser(a_sheet).run()
            a_pair = IpfriModelObjectBuilder(self.config, indicators, dates, countries).run()
            self.dataset_user_pairs.append(a_pair)

    def translate_model_objects_into_xml(self):
        for a_pair in self.dataset_user_pairs:
            ModelToXMLTransformer(dataset=a_pair.dataset,
                                  import_process="excell",
                                  user=a_pair.user).run()


    def determine_paths_to_files(self):
        path_pattern = self.config.get("IPFRI", "target_downloaded_file_pattern")
        if self.look_for_historical:
            self.determine_paths_to_every_available_year(path_pattern)
        else:
            self.determine_paths_to_current_year(path_pattern)

    def determine_paths_to_every_available_year(self, path_pattern):
        available_years = self.config.get("IPFRI", "available_years").split(",")
        for year in available_years:
            self.paths_to_files.append(path_pattern.replace("{year}", year))

    def determine_paths_to_current_year(self, path_pattern):
        year = self.config.get("AVAILABLE_YEARS", "year_to_look_for")
        candidate_file = path_pattern.replace("{year}", int(year))
        if os.path.exists(candidate_file):
            self.paths_to_files.append(candidate_file)
        else:
            raise RuntimeError("It looks like there is no available actual info. IpfriImporter will stop it execution")


    def take_data_sheet_from_file_path(self, a_path):
        book = xlrd.open_workbook(a_path, encoding_override='latin-1')
        #We are assuming that the sheet with the data is placed the last in the book
        return book.sheet_by_index(book.nsheets - 1)


