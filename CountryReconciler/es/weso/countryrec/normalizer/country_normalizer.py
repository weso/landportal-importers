"""
Created on 10/02/2014

@author: Dani
"""

from es.weso.countryrec.entities.normalized_country import NormalizedCountry


class CountryNormalizer(object):
    def __init__(self, parsed_countries):
        self.parsed_countries = parsed_countries

    def normalize_country_by_un_code(self, un_code):
        for country in self.parsed_countries:
            if country.get_un_code() == un_code:
                return NormalizedCountry(country.get_name(), country.get_iso3())

    def normalize_country_by_en_name(self, en_name):
        return en_name

    def normalize_country_by_es_name(self, es_name):
        return es_name

    def normalize_country_by_fr_name(self, fr_name):
        return fr_name