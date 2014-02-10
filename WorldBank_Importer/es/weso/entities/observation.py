'''
Created on 18/12/2013

@author: Nacho
'''

class Observation(object):
    '''
    classdocs
    '''


    def __init__(self, observation_id = None, ref_time = None, issued = None,
                 computation = None, value = None, indicator = None, provider = None):
        '''
        Constructor
        '''
        self.observation_id = observation_id
        self.ref_time = ref_time
        self.issued = issued
        self.computation = computation
        self.value = value
        self.indicator = indicator
        self.provider = provider
        