'''
Created on 02/02/2014

@author: Miguel Otero
'''

from es.weso.entities.value import Value

class FloatValue(Value):
    '''
    classdocs
    '''


    def __init__(self, obs_status = None, value = None):
        '''
        Constructor
        '''
        super(FloatValue, self).__init__(obs_status)
        self.value = value
        
    def get_value(self):
        return self.value