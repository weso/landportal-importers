'''
Created on 31/01/2014

@author: Miguel Otero
'''

from lpentities.observation import Observation

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
        self._un_code = un_code
        self.is_part_of = is_part_of
        self.observations = []
    
    def __get_un_code(self):
        return self._un_code
    
    def __set_un_code(self, un_code):
        try:
            self._un_code = int(un_code)
        except:
            raise ValueError("UN CODE must be an integer")
        
    un_code = property(fget=__get_un_code,
                      fset=__set_un_code,
                      doc="The un code of the region")
    
    def add_observation(self, observation):
        if isinstance(observation, Observation):
            self.observations.append(observation)
            observation.region = self
        else:
            raise ValueError("Trying to append a non Observation value to Region")

        
    def get_dimension_string(self):
        return self.name