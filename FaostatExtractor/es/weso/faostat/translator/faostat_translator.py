"""
Created on 27/01/2014

@author: Dani
"""

import codecs
import os
import re

from lpentities.computation import Computation
from lpentities.user import User
from model2xml.model2xml import ModelToXMLTransformer
from reconciler.country_reconciler import CountryReconciler

from .indicator_needed_resolver import IndicatorNeededResolver
from .model_object_builder import ModelObjectBuilder
from .relative_registers_calculator import RelativeRegistersCalculator
from .translator_const import TranslatorConst


class FaostatTranslator(object):
    """
    classdocs

    """

    def __init__(self, log, config, look_for_historical):
        """
        Constructor

        """
        self._log = log
        self._config = config
        self._look_for_historical = look_for_historical
        self._observations = []  # it will contains all the data encapsuled in model objects
        self._needed_indicators = IndicatorNeededResolver(self._config, self._log).run()
        self._land_area_reference = {}
        self._reconciler = CountryReconciler()
        # It will contain data with the general country areas
        # The key of the dictionary will be formed by
        # country_name + year, and will contain the land_area
        # data associated to this value par


    def run(self):
        """
        Steps:
        
        Turn into list with fields
        Build model objects
        
        """

        registers = self.turn_raw_data_into_registers(self._look_for_historical)
        registers += RelativeRegistersCalculator(self._log,
                                                 registers,
                                                 self._land_area_reference,
                                                 self.key_for_land_area_ref).run()  # The last arg. is a function
        builder = ModelObjectBuilder(registers, self._config, self._log, self._reconciler, self._look_for_historical)
        try:
            dataset_model = builder.run()
            self.generate_xml_from_dataset_model(dataset_model)
            self._update_config_values(builder)
        except BaseException as e:
            self._log.error("Error while trying to sned xml to the receiver: " + e.message)
            raise e


    def _update_config_values(self, object_builder):
        self._config.set("TRANSLATOR", "obs_int", object_builder._obs_int)
        self._config.set("TRANSLATOR", "dat_int", object_builder._dat_int)
        self._config.set("TRANSLATOR", "sli_int", object_builder._sli_int)
        self._config.set("TRANSLATOR", "igr_int", object_builder._igr_int)
        self._config.set("HISTORICAL", "first_valid_year", int(object_builder._last_checked_year) + 1)
        #lastchecked + 1 == firstvalid



    def generate_xml_from_dataset_model(self, dataset_model):
        xml_gen = ModelToXMLTransformer(dataset_model, ModelToXMLTransformer.CSV
                                        , self.build_user_object(dataset_model.source.organization)
                                        , self._path_to_data_file())
        xml_gen.run()

    def _path_to_data_file(self):
        base_dir = self._config.get("FAOSTAT", "data_file_path")
        return os.path.abspath(os.path.join(base_dir, os.listdir(base_dir)[0]))


    def build_user_object(self, organization):
        user = User(user_login=self._config.get("USER", "login"))
        user.organization = organization
        return user


    def get_csv_file_name(self):
        csv_file = os.listdir(self._config.get("FAOSTAT", "data_file_path"))[0]
        if csv_file[-4:] != '.csv':
            raise RuntimeError("Unexpected content while looking for indicators\
                . CSV file expected but {0} was found".format(csv_file))
        return self._config.get("FAOSTAT", "data_file_path") + "/" + csv_file


    def turn_raw_data_into_registers(self, look_for_historical):
        raw_data_file = codecs.open(self.get_csv_file_name(), encoding='latin-1')
        lines = raw_data_file.readlines()
        raw_data_file.close()
        result = []
        for i in range(1, len(lines)):
            propper_line = lines[i].encode(encoding="utf-8")
            try:
                candidate_register = self.create_field_list(propper_line, i + 1)
                if self.pass_filters(candidate_register, look_for_historical):
                    self.actualize_land_area_data_if_needed(candidate_register)
                    result.append(self.create_field_list(propper_line, i + 1))
            except RuntimeError as e:
                self._log.info("While parsing a row form the csv_file: {0}. Row will be ignored".format(e.message))
        return result


    def actualize_land_area_data_if_needed(self, candidate_register):
        if not candidate_register[TranslatorConst.ITEM_CODE] == TranslatorConst.CODE_LAND_AREA:
            return
        key = self.key_for_land_area_ref(candidate_register[TranslatorConst.COUNTRY_CODE],
                                         candidate_register[TranslatorConst.YEAR])
        if not key in self._land_area_reference:
            self._land_area_reference[key] = candidate_register[TranslatorConst.VALUE]
        else:
            raise RuntimeError("Duplicated land area value for country {0} and \
                year {1}. The program will continue ignoring the new value, but\
                it looks like the data is corrupted".format(candidate_register[TranslatorConst.COUNTRY],
                                                            candidate_register[TranslatorConst.YEAR]))

    @staticmethod
    def key_for_land_area_ref(country_code, year):
        return str(country_code) + "_" + str(year)

    def pass_filters(self, candidate_register, look_for_historical):
        """
        Steps:
        Filter if needed by date
        Filter by indicator needed
        Filter by recognized country


        """
        if not look_for_historical and not self.pass_filter_current_date(candidate_register):
            return False
        elif not self.pass_filter_indicator_needed(candidate_register):
            return False
        elif self._reconciler.get_country_by_faostat_code(candidate_register[TranslatorConst.COUNTRY_CODE]) is None:
            return False
        return True

    def pass_filter_current_date(self, candidate_register):
        if int(candidate_register[TranslatorConst.YEAR]) >= self._config.get("HISTORICAL", "first_valid_year"):
            return True
        return False

    def pass_filter_indicator_needed(self, candidate_register):
        if candidate_register[TranslatorConst.ITEM] in self._needed_indicators:
            return True
        return False


    def create_field_list(self, line, index):
        primitive_data = line.split(",\"")  # The CSV file separate fields with comma, but there are commas inside
        # some fields, so we can split by ',' .All the fields but the first
        # starts with the character '"', so if we split by ",\"", we get the
        # expected result. We have to consider this when parsing values
        if len(primitive_data) != TranslatorConst.EXPECTED_NUMBER_OF_COLS:
            raise RuntimeError("Row {0} contains a non expected number of fileds. \
                        The row must be ignored".format(str(index)))

        return self.parse_register_fields(primitive_data)



    def parse_register_fields(self, primitive_data):
        result = []
        result.insert(TranslatorConst.COUNTRY_CODE,
                      self._parse_country_code(primitive_data[TranslatorConst.COUNTRY_CODE]))
        result.insert(TranslatorConst.COUNTRY, self._parse_country(primitive_data[TranslatorConst.COUNTRY]))
        result.insert(TranslatorConst.ITEM_CODE, self._parse_item_code(primitive_data[TranslatorConst.ITEM_CODE]))
        result.insert(TranslatorConst.ITEM, self._parse_item(primitive_data[TranslatorConst.ITEM]))
        result.insert(TranslatorConst.ELEMENT_GROUP,
                      self._parse_element_group(primitive_data[TranslatorConst.ELEMENT_GROUP]))
        result.insert(TranslatorConst.ELEMENT_CODE,
                      self._parse_element_code(primitive_data[TranslatorConst.ELEMENT_CODE]))
        result.insert(TranslatorConst.ELEMENT, self._parse_element(primitive_data[TranslatorConst.ELEMENT]))
        result.insert(TranslatorConst.YEAR, self._parse_year(primitive_data[TranslatorConst.YEAR]))
        result.insert(TranslatorConst.UNIT, self._parse_unit(primitive_data[TranslatorConst.UNIT]))
        result.insert(TranslatorConst.VALUE, self._parse_value(primitive_data[TranslatorConst.VALUE]))
        result.insert(TranslatorConst.FLAG, self._parse_flag(primitive_data[TranslatorConst.FLAG]))
        result.insert(TranslatorConst.COMPUTATION_PROCESS, self._get_non_parsed_computation_process())

        return result


    @staticmethod
    def _get_non_parsed_computation_process():
        return Computation.RAW

    @staticmethod
    def _parse_country_code(primitive_data):
        """
        If the received chain does not contain '"', it should be casteable
        to int. If it does, we have first to remove that '"' characters.
        They shloud be at the begening and the end of the string

        """
        if not '"' in primitive_data:
            return int(primitive_data)
        else:
            return int(primitive_data[1:-1])

    @staticmethod
    def _parse_country(primitive_data):
        """
        We are receiving the name of a country with an '"' at the end

        """
        return primitive_data[:-1]

    @staticmethod
    def _parse_item_code(primitive_data):
        """
        We are receiving an string containing a int number with a "'" at the end

        """
        return int(primitive_data[:-1])

    @staticmethod
    def _parse_item(primitive_data):
        """
        We are receiving the name of an item with an '"' at the end

        """
        return primitive_data[:-1]

    @staticmethod
    def _parse_element_group(primitive_data):
        """
        We are receiving an string containing a int number with a "'" at the end

        """
        return int(primitive_data[:-1])


    @staticmethod
    def _parse_element_code(primitive_data):
        """
        We are receiving an string containing a int number with a "'" at the end

        """
        return int(primitive_data[:-1])

    @staticmethod
    def _parse_element(primitive_data):
        """
        We are receiving the name of an element with an '"' at the end

        """
        return primitive_data[:-1]

    @staticmethod
    def _parse_year(primitive_data):
        """
        We are receiving an string containing a int number with a "'" at the end

        """
        return int(primitive_data[:-1])

    @staticmethod
    def _parse_unit(primitive_data):
        """
        We are receiving the name of the measure unit with an '"' at the end

        """
        return primitive_data[:-1]

    @staticmethod
    def _parse_value(primitive_data):
        """
        We are receiving a number with an " at the end and possibly a "."
        because of ot presentation format. Ej: 1000 = 1.000
        I THINK it works like this. It also coulb be expressing decimals.
        We have to check that

        """
        return re.sub('\.|\"', "", primitive_data)

    @staticmethod
    def _parse_flag(primitive_data):
        """
        We are receiving a flag sequence with an '"' at the end and a whitespace

        """
        return primitive_data[:-2]