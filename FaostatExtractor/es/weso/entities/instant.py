'''
Created on 02/02/2014

@author: Miguel Otero
'''

from es.weso.entities.time import Time

class Instant(Time):
    '''
    classdocs
    '''


    def __init__(self, instant = None):
        '''
        Constructor
        '''
        self.instant = instant
        
    
    def get_time_string(self):
        return self.instant.strftime("%Y-%m-%dT%H:%M:%S")