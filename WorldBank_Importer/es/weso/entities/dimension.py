'''
Created on 07/02/2014

@author: Miguel Otero
'''

from abc import ABCMeta, abstractmethod

class Dimension(object):
    '''
    classdocs
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_dimension_string(self): pass
        