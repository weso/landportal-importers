__author__ = 'Dani'


class Deal(object):

    def __init__(self, target_country=None, hectares=None, date=None, sectors=None):
        self.target_country = target_country
        self.hectares = hectares
        self.date = date
        self.sectors = sectors


