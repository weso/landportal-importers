__author__ = 'Dani'


class NoNewDataAvailableError(RuntimeError):

    def __init__(self, msg):
        self.message = msg
