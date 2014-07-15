__author__ = 'Dani'

import xlrd

from model2xml.model2xml import ModelToXMLTransformer
from .parser.parser import Parser
from .object_builder.model_object_builder import IpfriModelObjectBuilder

import os.path


class IpfriTranslator(object):

    def __init__(self, log, config, look_for_historical=True):
        self._paths_to_files = []
        self._log = log
        self._config = config
        self._look_for_historical = look_for_historical
        self._dataset_user_file_groups = []

    def run(self):
        try:
            self.determine_paths_to_files()
        except BaseException as e:
            raise RuntimeError("While trying to determine paths to files to parse: " + e.message)
        try:
            self._initialize_ids_propperly()
        except BaseException as e:
            raise RuntimeError("While trying to initialize ids to create entities: " + e.message)
        try:
            self.translate_files_into_model_objects()
        except BaseException as e:
            raise RuntimeError("While trying to generate model objects: " + e.message)
        try:
            self.translate_model_objects_into_xml()
        except BaseException as e:
            raise RuntimeError("While trying to turn model objects into xml: " + e.message)
        self._log.info("Final xml succesfully sent to the Receiver module")

    def _initialize_ids_propperly(self):
        """
        The object builders will take values for assign ids from the config. But there will be several
        instances of objects builders, all of them using the same config. We will manage the config here,
        before starting the execution of the object builders.

        """

        if self._look_for_historical:  # restart the conunt
            self._config.set("TRANSLATOR", "obs_int", "0")
            self._config.set("TRANSLATOR", "sli_int", 0)
            self._config.set("TRANSLATOR", "igr_int", 0)
            self._config.set("TRANSLATOR", "dat_int", 0)
        else:
            pass  # The value that we have in the config is valid in this case


    def translate_files_into_model_objects(self):
        i = 0
        for a_path in self._paths_to_files:
            i += 1
            a_sheet = self.take_data_sheet_from_file_path(a_path)
            indicators, dates, countries = Parser(a_sheet).run()
            a_group = IpfriModelObjectBuilder(self._log,
                                              self._config,
                                              indicators,
                                              dates,
                                              countries,
                                              os.path.abspath(a_path)).run()
            self._dataset_user_file_groups.append(a_group)

    def translate_model_objects_into_xml(self):
        for a_group in self._dataset_user_file_groups:
            ModelToXMLTransformer(dataset=a_group.dataset,
                                  import_process=ModelToXMLTransformer.XLS,
                                  user=a_group.user,
                                  path_to_original_file=a_group.file_path).run()
            self._persist_config_values()


    def _persist_config_values(self):
        with open("./files/configuration.ini", "wb") as config_file:
            self._config.write(config_file)


    def determine_paths_to_files(self):
        path_pattern = self._config.get("IPFRI", "target_downloaded_file_pattern")
        if self._look_for_historical:
            self.determine_paths_to_every_available_year(path_pattern)
        else:
            self.determine_paths_to_current_year(path_pattern)

    def determine_paths_to_every_available_year(self, path_pattern):
        available_years = self._config.get("IPFRI", "available_years").split(",")
        for year in available_years:
            self._paths_to_files.append(path_pattern.replace("{year}", year))

    def determine_paths_to_current_year(self, path_pattern):
        year = self._config.get("AVAILABLE_YEARS", "year_to_look_for")
        candidate_file = path_pattern.replace("{year}", int(year))
        if os.path.exists(candidate_file):
            self._paths_to_files.append(candidate_file)
        else:
            raise RuntimeError("It looks like there is no available actual info. IpfriImporter will stop its execution")


    @staticmethod
    def take_data_sheet_from_file_path(a_path):
        book = xlrd.open_workbook(a_path, encoding_override='latin-1')
        #We are assuming that the sheet with the data is placed the last in the book
        return book.sheet_by_index(book.nsheets - 1)
