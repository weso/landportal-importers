
"""
Created on 18/02/2014

@author: Miguel Otero
"""



class IndicatorGroup(object):

    def __init__(self, chain_for_id, int_for_id, compound_indicator=None, observations=None):

        self.compound_indicator = compound_indicator
        self.observations = observations

        self.group_id = self._generate_id(chain_for_id, int_for_id)

    @staticmethod
    def _generate_id(chain_for_id, int_for_id):
        return "IGR" + chain_for_id.upper() + str(int_for_id).upper()

    def add_observation(self, observation):
        self.observations.append(observation)
        observation.group = self