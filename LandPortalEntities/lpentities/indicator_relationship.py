'''
Created on 02/02/2014

@author: Miguel Otero
'''
from lpentities.indicator import Indicator


class IndicatorRelationship(object):
    '''
    classdocs
    '''


    def __init__(self, source, target):
        '''
        Constructor
        '''
        self._source = source
        self._target = target
        
    def __get_source(self):
        return self._source
    
    def __set_source(self, source):
        if isinstance(source, Indicator):
            self._source = source
        else:
            raise ValueError("Expected Indicator object as source in a relationship")
        
    source = property(fget=__get_source, fset=__set_source, doc="Source of the relationship")
    
    def __get_target(self):
        return self._target
    
    def __set_target(self, target):
        if isinstance(target, Indicator):
            self._target = target
        else:
            raise ValueError("Expected Indicator object as target in a relationship")
        
    target = property(fget=__get_target, fset=__set_target, doc="Target of the relationship")
    