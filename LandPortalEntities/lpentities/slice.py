'''
Created on 02/02/2014

@author: Miguel Otero
'''
from lpentities.dataset import Dataset
from lpentities.dimension import Dimension
from lpentities.indicator import Indicator
from lpentities.observation import Observation


class Slice(object):
    '''
    classdocs
    '''


    def __init__(self, chain_for_id, int_for_id, dimension=None, dataset=None, indicator=None):
        '''
        Constructor

        '''

        self._dataset = dataset
        self._indicator = indicator
        self._dimension = dimension

        self.observations = []

        self.slice_id = self._generate_id(chain_for_id, int_for_id)

    def __get_dataset(self):
        return self._dataset
    
    def __set_dataset(self, dataset):
        if isinstance(dataset, Dataset) :
            self._dataset = dataset
        else:
            raise ValueError("Expected Dataset object in Slice")
        
    dataset = property(fget=__get_dataset,
                      fset=__set_dataset,
                      doc="The dataset for the slice")
    
    def __get_indicator(self):
        return self._indicator
    
    def __set_indicator(self, indicator):
        if isinstance(indicator, Indicator) :
            self._indicator = indicator
        else:
            raise ValueError("Expected Indicator object in Slice")
        
    indicator = property(fget=__get_indicator,
                      fset=__set_indicator,
                      doc="The indicator for the slice")
    
    def __get_dimension(self):
        return self._dimension
    
    def __set_dimension(self, dimension):
        if isinstance(dimension, Dimension) :
            self._dimension = dimension
        else:
            raise ValueError("Expected Dimension object in Slice")
        
    dimension = property(fget=__get_dimension,
                      fset=__set_dimension,
                      doc="The dimension for the slice")
    
    @staticmethod
    def _generate_id(chain_for_id, int_for_id):
        return "SLI" + chain_for_id.upper() + str(int_for_id).upper()
        
    def add_observation(self, observation):
        if isinstance(observation, Observation):
            self.observations.append(observation)
            observation.data_slice = self
        else:
            raise ValueError("Trying to append non observation object to slice")