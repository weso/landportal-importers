'''
Created on 18/12/2013

@author: Nacho
'''

class Observation(object):
    '''
    classdocs
    '''

    def __init__(self,observation_id = "obs", ref_time=None, issued=None, computation=None, value=None, 
                 measure_unit=None, indicator=None, data_slice=None, provider=None):
        '''
        Constructor
        '''
        self.observation_id = observation_id
        self.ref_time = ref_time
        self.issued = issued
        self.computation = computation
        self.value = value
        self.measure_unit = measure_unit
        self.indicator = indicator
        self.data_slice = data_slice
        self.provider = provider
  
        