__author__ = 'Dani'


class XmlRegister(object):

    def __init__(self, country):
        self.country = country  # lpentities.country.Country objetc
        self._available_data = []  # List of Indicator_data objects
        pass


class IndicatorData(object):

    def __init__(self, indicator_code, value, date):
        self.indicator_code = indicator_code
        self.value = value
        self.date = date





