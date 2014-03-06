__author__ = 'Miguel Otero'


class ParsingError(RuntimeError):

    def __init__(self, msg):
      self.message = msg