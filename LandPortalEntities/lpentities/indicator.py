'''
Created on 19/12/2013

@author: Nacho
'''


class Indicator(object):
    '''
    classdocs
    '''

    def __init__(self, chain_for_id, int_for_id, name=None, description=None,
                 dataset=None, measurement_unit=None):
        '''
        Constructor
        '''
        self.name = name
        self._chain_for_id = chain_for_id
        self._int_for_id = int_for_id
        self.description = description
        self.dataset = dataset
        self.measurement_unit = measurement_unit

        self.indicator_id = self._generate_id()


    def _generate_id(self):
        return "ind_" + self._chain_for_id + "_" + str(self._int_for_id)