'''
Created on 19/12/2013

@author: Nacho
'''


class Indicator(object):
    '''
    classdocs
    '''

    def __init__(self, indicator_id=None, name=None, description=None,
                 dataset=None, measurement_unit=None):
        '''
        Constructor
        '''
        self.name = name
        self.indicator_id = indicator_id
        self.description = description
        self.dataset = dataset
        self.measurement_unit = measurement_unit