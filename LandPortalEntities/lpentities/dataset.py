'''
Created on 02/02/2014

@author: Miguel Otero
'''


class Dataset(object):
    '''
    classdocs
    '''

    def __init__(self, dataset_id=None, name=None, frequency=None,
                 license_type=None, source=None):
        '''
        Constructor
        '''
        self.dataset_id = dataset_id
        self.name = name
        self.frequency = frequency
        self.license_type = license_type
        self.source = source
        self.slices = []
        self.observations = []
        self.indicators = []

    def add_slice(self, data_slice):
        self.slices.append(data_slice)
        data_slice.dataset = self

    def add_observation(self, observation):
        self.observations.append(observation)
        observation.dataset = self

    def add_indicator(self, indicator):
        self.indicators.append(indicator)
        indicator.dataset = self