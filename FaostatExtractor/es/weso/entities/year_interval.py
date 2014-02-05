'''
Created on 02/02/2014

@author: Miguel Otero
'''

from es.weso.entities.interval import Interval

class YearInterval(Interval):
    '''
    classdocs
    '''


    def __init__(self, start_time, end_time, year):
        '''
        Constructor
        '''
        super(YearInterval, self).__init__(start_time, end_time)
        self.year = year
        