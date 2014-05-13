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
        super(YearInterval, self).__init__(Interval.YEARLY, year, year)
        self._year = year
    
    def __get_year(self):
        return self._year
    
    def __set_year(self, year):
        try:
            self._year = int(year)
        except:
            raise ValueError("Year must be an integer")
        
    year = property(fget=__get_year,
                      fset=__set_year,
                      doc="The year for the interval")
    
    def get_time_string(self):
        return str(self.year)