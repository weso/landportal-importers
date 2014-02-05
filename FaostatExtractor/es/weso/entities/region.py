'''
Created on 31/01/2014

@author: Miguel Otero
'''

class Region(object):
    '''
    classdocs
    '''


    def __init__(self, name, is_part_of):
        '''
        Constructor
        '''
        self.name = name
        self.is_part_of = is_part_of
        self.observations = []
        
    def add_observation(self, observation):
        self.observations.append(observation)
        observation.region = self