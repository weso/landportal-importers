__author__ = 'Dani'


class DealAnalyserEntry(object):
    """
    The DealAnalyser will return a dict that saves under a key composed by Country and indicator
    certains group of entities.
    This class contains all this elements: an indicator, a date (int), a country (country entity) and a value

    """

    def __init__(self, indicator, date, country, value):
        self.indicator = indicator
        self.date = date
        self.country = country
        self.value = value
