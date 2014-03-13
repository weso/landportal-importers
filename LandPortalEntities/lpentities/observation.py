'''
Created on 18/12/2013

@author: Nacho
'''

class Observation(object):
    '''
    classdocs
    '''

    def __init__(self, chain_for_id, int_for_id, ref_time=None, issued=None,
                 computation=None, value=None, indicator=None, dataset=None):
        '''
        Constructor
        '''

        self._chain_for_id = chain_for_id
        self._int_for_id = int_for_id
        self.ref_time = ref_time
        self.issued = issued
        self.computation = computation
        self.value = value
        self.indicator = indicator
        self.dataset = dataset
        self.group = None
        self.indicator_group = None

        self.observation_id = self._generate_id()

    def _generate_id(self):
        return "obs_" + self._chain_for_id + "_" + str(self._int_for_id)