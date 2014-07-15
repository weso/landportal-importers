__author__ = 'Dani'


class XmlRegister(object):

    def __init__(self, country):
        self.country = country  # lpentities.country.Country objetc
        self._available_data = []  # List of Indicator_data objects


    def add_indicator_data(self, indicator_data):
        self._available_data.append(indicator_data)


    def get_available_data(self):
        return self._available_data


class IndicatorData(object):



    def __init__(self, indicator_code, value, date):
        """
        Constructor

        """
        self.indicator_code = indicator_code
        self.value = value
        self.date = date  # It is supoused to be an lpentities object: a YearInterval or an Interval






