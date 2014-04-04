'''
Created on 31/01/2014

@author: Miguel Otero
'''

from .dimension import Dimension

class Region(Dimension):
    '''
    classdocs
    '''


    def __init__(self, name=None, is_part_of=None, un_code=None):
        '''
        Constructor
        '''
        self.name = name
        self.un_code = un_code
        self.is_part_of = is_part_of
        self.observations = []
        
    def add_observation(self, observation):
        self.observations.append(observation)
        observation.region = self
        
    def get_dimension_string(self):
        return self.name