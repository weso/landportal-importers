'''
Created on 02/02/2014

@author: Miguel Otero
'''

from es.weso.entities.dimension import Dimension
from abc import ABCMeta, abstractmethod

class Time(Dimension):
    '''
    classdocs
    '''
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_time_string(self):
        pass
    
    def get_dimension_string(self):
        return self.get_time_string()