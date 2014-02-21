"""
Created on 10/02/2014

@author: Dani
"""

from es.weso.countryrec.parser.file_parser import FileParser
from es.weso.countryrec.normalizer.country_normalizer import CountryNormalizer


class CountryReconcilier(object):

    def __init__(self):
        self.country_normalizer = self.create_normalizer()

    @staticmethod
    def create_normalizer():
        file_parser = FileParser()
        return CountryNormalizer(file_parser.run())

    def get_country_by_un_code(self, un_code):
        return self.country_normalizer.normalize_country_by_un_code(un_code)

    def get_country_by_name(self, name):
        return self.country_normalizer.normalize_country_by_name(name)