'''
Created on 02/02/2014

@author: Miguel Otero
'''
from lpentities.indicator import Indicator


class Dataset(object):
    """
    classdocs

    """
    MONTHLY = "freq-M"
    YEARLY = "freq-A"
    THREE_YEARS = "freq-A"  # TODO: it could change

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
        return "DAT" + chain_for_id.upper() + str(int_for_id).upper()

    def add_slice(self, data_slice):
        self.slices.append(data_slice)
        data_slice.dataset = self

        
    def add_observation(self, observation):
        self.observations.append(observation)
        observation.dataset = self

        
    def add_indicator(self, indicator):
        if isinstance(indicator, Indicator):
            self.indicators.append(indicator)
            indicator.dataset = self
        else:
            raise ValueError("Trying to append a non indicator object to datase")