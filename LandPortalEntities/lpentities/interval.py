'''
Created on 02/02/2014

@author: Miguel Otero
'''

from .time import Time


class Interval(Time):
    '''
    classdocs
    '''
    MONTHLY = "freq-M"
    YEARLY = "freq-A"

    def __init__(self, frequency=YEARLY, start_time=None, end_time=None):
        '''
        Constructor
        '''
        self._frequency = frequency
        self.start_time = start_time
        self.end_time = end_time
    
    def __get_frequency(self):
        return self._frequency
    
    def __set_frequency(self, frequency):
        if frequency == self.MONTHLY or frequency == self.YEARLY:
            self._frequency = frequency
        else:
            raise ValueError("Interval frequency not one of the given ones")
        
    frequency = property(fget=__get_frequency, fset=__set_frequency, doc="Frequency of the interval")
    
    def get_time_string(self):
        return str(self.start_time) + '-' + str(self.end_time)