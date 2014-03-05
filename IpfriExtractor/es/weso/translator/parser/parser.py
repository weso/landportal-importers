__author__ = 'Dani'

from .indicators_parser import IndicatorsParser
from .dates_parser import DatesParser
from .countries_parser import CountriesParser
class Parser(object):

    def __init__(self, sheet):
        self.sheet = sheet

    def run(self):
        indicators = IndicatorsParser(self.sheet).run()
        dates = DatesParser(self.sheet).run()
        countries = CountriesParser(self.sheet).run()

        return indicators, dates, countries
