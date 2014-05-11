'''
Created on 02/02/2014

@author: Miguel Otero
'''


class Dataset(object):
    """
    classdocs

    """
    MONTHLY = "http://purl.org/linked-data/sdmx/2009/code#freq-M"
    YEARLY = "http://purl.org/linked-data/sdmx/2009/code#freq-A"
    THREE_YEARS = "http://purl.org/linked-data/sdmx/2009/code#freq-UNKNOKNW"  # TODO: temporal. Talk with Labra

    def __init__(self, chain_for_id, int_for_id, frequency=None,
                 license_type=None, source=None):
        '''
        Constructor
        '''
        self.frequency = frequency
        self.license_type = license_type
        self.source = source

        self.slices = []
        self.observations = []
        self.indicators = []

        self.dataset_id = self._generate_id(chain_for_id, int_for_id)

    @staticmethod
    def _generate_id(chain_for_id, int_for_id):
        return "DAT" + chain_for_id.upper() + "_" + str(int_for_id).upper()

    def add_slice(self, data_slice):
        self.slices.append(data_slice)
        data_slice.dataset = self

    def add_observation(self, observation):
        self.observations.append(observation)
        observation.dataset = self

    def add_indicator(self, indicator):
        self.indicators.append(indicator)
        indicator.dataset = self
