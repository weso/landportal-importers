"""
Created on 10/02/2014

@author: Dani
"""
from reconciler.exceptions.unknown_country_error import UnknownCountryError

from reconciler.file_parser import FileParser
from reconciler.country_normalizer import CountryNormalizer


class CountryReconciler(object):

    def __init__(self):
        self.parsed_countries = FileParser().run()
        self.normalizer = CountryNormalizer()


    def get_country_by_iso2(self, iso2):
        for country in self.parsed_countries:
            if country.iso2 == iso2:
                return country.model_object
        raise UnknownCountryError("Unknown country for ISO2 " + iso2)


    def get_country_by_faostat_code(self, faostat_code):
        for country in self.parsed_countries:
            if country.faostat_code == faostat_code:
                return country.model_object
        raise UnknownCountryError('Unknown country for FAOSTAT code ' + str(faostat_code))


    def get_country_by_un_code(self, un_code):
        for country in self.parsed_countries:
            if country.un_code == un_code:
                return country.model_object
        raise UnknownCountryError('Unknown country for UN code ' + str(un_code))


    def get_country_by_en_name(self, name):
        normalized_parameter = self.normalizer.normalize_country_by_en_name(name)
        #Check short names
        for parsed_country in self.parsed_countries:
            if CountryReconciler._has_content(parsed_country.sname_en):
                normalized_parsed_country = self.normalizer.normalize_country_by_en_name(parsed_country.sname_en)
                if normalized_parameter == normalized_parsed_country:
                    return parsed_country.model_object  # 1st possible return
        #Check long names
        for parsed_country in self.parsed_countries:
            if CountryReconciler._has_content(parsed_country.lname_en):
                normalized_parsed_country = self.normalizer.normalize_country_by_en_name(parsed_country.lname_en)
                if normalized_parameter == normalized_parsed_country:
                    return parsed_country.model_object  # 2nd possible return
        #Check alt names
        for parsed_country in self.parsed_countries:
            if CountryReconciler._has_content(parsed_country.alt_en_name1):
                normalized_parsed_country = self.normalizer.normalize_country_by_en_name(parsed_country.alt_en_name1)
                if normalized_parameter == normalized_parsed_country:
                    return parsed_country.model_object  # 3rd possible return
        for parsed_country in self.parsed_countries:
            if CountryReconciler._has_content(parsed_country.alt_en_name2):
                normalized_parsed_country = self.normalizer.normalize_country_by_en_name(parsed_country.alt_en_name2)
                if normalized_parameter == normalized_parsed_country:
                    return parsed_country.model_object  # 4th possible return

        raise UnknownCountryError("Impossible to find coincidences in country names with '{0}'".format(name))


    def get_country_by_es_name(self, name):
        normalized_parameter = self.normalizer.normalize_country_by_es_name(name)
        print "ES-----------"
        print normalized_parameter
        print "ES-----------"

        #Check short name
        for country in self.parsed_countries:
            if self._has_content(country.sname_es):
                normalized_parsed_country = self.normalizer.normalize_country_by_es_name(country.sname_es)
                if normalized_parameter == normalized_parsed_country:
                    return country.model_object  # 1st possible return
        #Check long name
        for country in self.parsed_countries:
            if self._has_content(country.lname_es):
                normalized_parsed_country = self.normalizer.normalize_country_by_es_name(country.lname_es)
                if normalized_parameter == normalized_parsed_country:
                    return country.model_object  # 2nd possible return

        raise UnknownCountryError("Impossible to find coincidences in country names with " + name)

    def get_country_by_fr_name(self, name):
        normalized_parameter = self.normalizer.normalize_country_by_fr_name(name)
        #Check short name2
        for country in self.parsed_countries:
            if self._has_content(country.sname_fr):
                normalized_parsed_country = self.normalizer.normalize_country_by_fr_name(country.sname_fr)
                if normalized_parameter == normalized_parsed_country:
                    return country.model_object  # 1st possible return
        #Check long name
        for country in self.parsed_countries:
            if self._has_content(country.lname_fr):
                normalized_parsed_country = self.normalizer.normalize_country_by_fr_name(country.lname_fr)
                if normalized_parameter == normalized_parsed_country:
                    return country.model_object  # 2nd possible return

        raise UnknownCountryError("Impossible to find coincidences in country names with '{0}'".format(name))

    @staticmethod
    def _has_content(value):
        if value is None:
            return False
        elif value == "":
            return False
        return True