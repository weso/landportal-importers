"""
Created on 21/04/2014

@author: Dani
"""
from es.weso.faogenderextractor.extractor.model_objects_management.model_object_builder import ModelObjectBuilder

from reconciler.country_reconciler import CountryReconciler
from es.weso.faogenderextractor.extractor.xml_management.countries_xml_extractor import CountriesXmlExtractor
from es.weso.faogenderextractor.extractor.xml_management.xml_content_parser import XmlContentParser


class FaoGenderExtractor(object):
    """
    Classdocs

    """


    def __init__(self, log, config, look_for_historical=True):
        """
        Constructor

        """
        self._log = log
        self._config = config
        self._reconciler = CountryReconciler()
        self._look_for_historical = look_for_historical

    def run(self):
        """
        Steps.
         - Get the list of all the countries
         - Make a query to the rest API for each country
         - Process the xml response, turning it into intermidiate objetcs
         - Turn that objects into model ones
         - Send to model2xml

        """
        xml_responses = self._get_xml_info_for_all_countries()
        registers = self._turn_responses_into_register_objects(xml_responses)
        self._build_model_objects_from_registers(registers)


    def _build_model_objects_from_registers(self, registers):
        ModelObjectBuilder(self._log, self._config, registers).run()


    def _get_xml_info_for_all_countries(self):
        return CountriesXmlExtractor(self._log, self._config, self._reconciler).run()

    def _turn_responses_into_register_objects(self, responses):
        return XmlContentParser(log=self._log,
                                config=self._config,
                                reconciler=self._reconciler,
                                responses=responses,
                                look_for_historical=self._look_for_historical).run()

    
    