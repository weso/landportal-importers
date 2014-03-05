'''
Created on 02/02/2014

@author: Miguel Otero
'''

from .interval import Interval

class YearInterval(Interval):
    '''
    classdocs
    '''


    def __init__(self, year):
        """
        Constructor

        """
        super(YearInterval, self).__init__(year, year)
        self.year = year
    
    def get_time_string(self):
        return str(self.year)