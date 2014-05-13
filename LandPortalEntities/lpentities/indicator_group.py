
"""
Created on 18/02/2014

@author: Miguel Otero
"""
from lpentities.observation import Observation
from lpentities.compound_indicator import CompoundIndicator


class IndicatorGroup(object):

    def __init__(self, chain_for_id, int_for_id, compound_indicator=None, observations=None):

        self._compound_indicator = compound_indicator
        self.observations = observations

        self.group_id = self._generate_id(chain_for_id, int_for_id)

    def __get_compound_indicator(self):
        return self._compound_indicator
    
    def __set_compound_indicator(self, compound_indicator):
        if isinstance(compound_indicator, CompoundIndicator):
            self._compound_indicator = compound_indicator
        else:
            raise ValueError("Trying to associate a non CompoundIndicator object to indicator group")
        
    compound_indicator = property(fget=__get_compound_indicator, fset=__set_compound_indicator, doc="Compound indicator of the group")
    
    @staticmethod
    def _generate_id(chain_for_id, int_for_id):
        return "IGR" + chain_for_id.upper() + str(int_for_id).upper()

    def add_observation(self, observation):
        if isinstance(observation, Observation):
            self.observations.append(observation)
            observation.group = self
        else:
            raise ValueError("Trying to append a non Observation object to indicator group")