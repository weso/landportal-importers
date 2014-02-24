'''
Created on 02/02/2014

@author: Miguel Otero
'''

from es.weso.entities.interval import Interval

class YearInterval(Interval):
    '''
    classdocs
    '''


    def __init__(self, start_time = None, end_time = None, year = None):
        '''
        Constructor
        '''
        super(YearInterval, self).__init__(start_time, end_time)
        self.year = year
    
    def get_time_string(self):
        return str(self.year)