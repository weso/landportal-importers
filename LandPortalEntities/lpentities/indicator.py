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
        self.description = description
        self.dataset = dataset
        self.measurement_unit = measurement_unit

        self.indicator_id = self._generate_id(chain_for_id, int_for_id)


    @staticmethod
    def _generate_id(chain_for_id, int_for_id):
        return "IND" + chain_for_id.upper() + str(int_for_id).upper()