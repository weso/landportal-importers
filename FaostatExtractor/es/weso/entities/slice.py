'''
Created on 02/02/2014

@author: Miguel Otero
'''

class Slice(object):
    '''
    classdocs
    '''


    def __init__(self, slice_id = None, dimension = None, dataset = None, indicator = None):
        '''
        Constructor
        '''
        self.dataset = dataset
        self.indicator = indicator
        self.slice_id = slice_id
        self.dimension = dimension
        self.observations = []
        
    def add_observation(self, observation):
        self.observations.append(observation)
        observation.data_slice = self