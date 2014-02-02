'''
Created on 02/02/2014

@author: Miguel Otero
'''

from es.weso.entities.time import Time

class Interval(Time):
    '''
    classdocs
    '''


    def __init__(self, start_time, end_time):
        '''
        Constructor
        '''
        self.start_time = start_time
        self.end_time = end_time
        