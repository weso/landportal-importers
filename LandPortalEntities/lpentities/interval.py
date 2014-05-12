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
        self.frequency = frequency
        self.start_time = start_time
        self.end_time = end_time
    
    def get_time_string(self):
        return str(self.start_time) + '-' + str(self.end_time)