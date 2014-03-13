
"""
Created on 18/02/2014

@author: Miguel Otero
"""



class IndicatorGroup(object):

    def __init__(self, chain_for_id, int_for_id, compound_indicator=None, observations=None):

        self._chain_for_id = chain_for_id
        self._int_for_id = int_for_id
        self.compound_indicator = compound_indicator
        self.observations = observations

        self.group_id = self._generate_id()

    def _generate_id(self):
        return "igr_" + self._chain_for_id + "_" + str(self._int_for_id)

    def add_observation(self, observation):
        self.observations.append(observation)
        observation.group = self