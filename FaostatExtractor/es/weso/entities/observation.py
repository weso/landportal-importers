'''
Created on 27/01/2014

@author: Miguel Otero
'''

class Observation(object):
    '''
    classdocs
    '''


    def __init__(self, value, ref_area, ref_time, issued,
                 computation, measure_unit, indicator, slice,
                 provider):
        '''
        Constructor
        '''
        self.value = value
        self.ref_area = ref_area
        self.ref_time = ref_time
        self.issued = issued
        self.computation = computation
        self.measure_unit = measure_unit
        self.indicator = indicator
        self.slice = slice
        self.provider = provider
        