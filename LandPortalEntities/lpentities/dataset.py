'''
Created on 02/02/2014

@author: Miguel Otero
'''
from lpentities.indicator import Indicator
from lpentities.observation import Observation
from lpentities.slice import Slice


class Dataset(object):
    """
    classdocs

    """
    MONTHLY = "freq-M"
    YEARLY = "freq-A"
    THREE_YEARS = "http://purl.org/linked-data/sdmx/2009/code#freq-UNKNOKNW"  # TODO: temporal. Talk with Labra

    def __init__(self, chain_for_id, int_for_id, frequency=None,
                 license_type=None, source=None):
        '''
        Constructor
        '''
        self._frequency = frequency
        self.license_type = license_type
        self.source = source

        self.slices = []
        self.observations = []
        self.indicators = []

        self.dataset_id = self._generate_id(chain_for_id, int_for_id)

    def __get_frequency(self):
        return self._frequency
    
    def __set_frequency(self, frequency):
        if frequency == self.MONTHLY or frequency == self.YEARLY or frequency == self.THREE_YEARS:
            self._frequency = frequency
        else:
            raise ValueError("Frequency not in the given values")
        
    frequency = property(fget=__get_frequency, fset=__set_frequency, doc="Update frequency of the dataset")
    

    @staticmethod
    def _generate_id(chain_for_id, int_for_id):
        return "DAT" + chain_for_id.upper() + "_" + str(int_for_id).upper()

    def add_slice(self, data_slice):
        if isinstance(data_slice, Slice):
            self.slices.append(data_slice)
            data_slice.dataset = self
        else:
            raise ValueError("Trying to append a non slice object to dataset")
        
    def add_observation(self, observation):
        if isinstance(observation, Observation):
            self.observations.append(observation)
            observation.dataset = self
        else:
            raise ValueError("Trying to append a non observation object to dataset")
        
    def add_indicator(self, indicator):
        if isinstance(indicator, Indicator):
            self.indicators.append(indicator)
            indicator.dataset = self
        else:
            raise ValueError("Trying to append a non indicator object to datase")