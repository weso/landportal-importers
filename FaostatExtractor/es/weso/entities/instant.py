'''
Created on 02/02/2014

@author: Miguel Otero
'''

from es.weso.entities.time import Time

class Instant(Time):
    '''
    classdocs
    '''


    def __init__(self, time):
        self.time = time
        
        '''
        Constructor
        '''
        