'''
Created on 18/12/2013

@author: Nacho
'''

class Observation(object):
    '''
    classdocs
    '''


    def __init__(self, ref_time, issued, computation, value, 
                 measure_unit, indicator, slice, provider):
        '''
        Constructor
        '''
        self.ref_time = ref_time
        self.issued = issued
        self.computation = computation
        self.value = value
        self.measure_unit = measure_unit
        self.indicator = indicator
        self.slice = slice
        self.provider = provider
        