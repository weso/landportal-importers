__author__ = 'Miguel Otero'


class UnknownCountryError(RuntimeError):

    def __init__(self, msg):
      self.message = msg