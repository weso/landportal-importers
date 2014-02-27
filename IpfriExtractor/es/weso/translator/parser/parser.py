__author__ = 'Dani'


class Parser(object):

    def __init__(self, sheet):
        self.sheet = sheet

    def run(self):
        indicators = IndicatorsParser(self.sheet).run()
        dates = DatesParser(self.sheet).run()
        countries = CountriesParser(self.sheet)

        return indicators, dates, countries
