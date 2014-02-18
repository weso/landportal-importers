"""
Created on 18/02/2014

@author: Miguel Otero
"""

from es.weso.entities.indicator import Indicator


class IndicatorGroup(Indicator):

    def __init__(self, indicator_id=None, name=None, description=None,
                 dataset=None, measurement_unit=None, group_id=None):
        super(IndicatorGroup, self).__init__(indicator_id, name, description,
                                             dataset, measurement_unit)
        self.group_id = group_id
        self.observations = []

    def add_observation(self, observation):
        self.observations.append(observation)
        observation.group = self