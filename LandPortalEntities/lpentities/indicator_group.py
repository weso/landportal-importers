
"""
Created on 18/02/2014

@author: Miguel Otero
"""



class IndicatorGroup(object):

    def __init__(self, group_id=None, compound_indicator=None, observations=None):
        self.group_id = group_id
        self.compound_indicator = compound_indicator
        self.observations = observations

    def add_observation(self, observation):
        self.observations.append(observation)
        observation.group = self