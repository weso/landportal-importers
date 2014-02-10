'''
Created on 02/02/2014

@author: Miguel Otero
'''

from es.weso.entities.time import Time

class Interval(Time):
    '''
    classdocs
    '''


    def __init__(self, start_time = None, end_time = None):
        '''
        Constructor
        '''
        self.start_time = start_time
        self.end_time = end_time
    
    def get_time_string(self):
        return str(self.start_time) + '-' + str(self.end_time)