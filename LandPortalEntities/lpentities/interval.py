'''
Created on 02/02/2014

@author: Miguel Otero
'''

from .time import Time


class Interval(Time):
    '''
    classdocs
    '''
    MONTHLY = "http://purl.org/linked-data/sdmx/2009/code#freq-M"
    YEARLY = "http://purl.org/linked-data/sdmx/2009/code#freq-A"

    def __init__(self, frequency = YEARLY, start_time=None, end_time=None):
        '''
        Constructor
        '''
        self.frequency = frequency
        self.start_time = start_time
        self.end_time = end_time
    
    def get_time_string(self):
        return str(self.start_time) + '-' + str(self.end_time)