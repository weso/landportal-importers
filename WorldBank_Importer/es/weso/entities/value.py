'''
Created on 02/02/2014

@author: Miguel Otero
'''

from abc import abstractmethod

class Value(object):
    '''
    classdocs
    '''


    def __init__(self, obs_status = None):
        '''
        Constructor
        '''
        self.obs_status = obs_status
    
    @abstractmethod
    def get_value(self): pass
        