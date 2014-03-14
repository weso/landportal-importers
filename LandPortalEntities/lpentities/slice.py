'''
Created on 02/02/2014

@author: Miguel Otero
'''

class Slice(object):
    '''
    classdocs
    '''


    def __init__(self, chain_for_id, int_for_id, dimension=None, dataset=None, indicator=None):
        '''
        Constructor

        '''

        self.dataset = dataset
        self.indicator = indicator
        self.dimension = dimension

        self.observations = []

        self.slice_id = self._generate_id(chain_for_id, int_for_id)

    @staticmethod
    def _generate_id(chain_for_id, int_for_id):
        return "SLI" + chain_for_id.upper() + str(int_for_id).upper()
        
    def add_observation(self, observation):
        self.observations.append(observation)
        observation.data_slice = self