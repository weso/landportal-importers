'''
Created on 02/02/2014

@author: Miguel Otero
'''


class DataSource(object):
    '''
    classdocs
    '''


    def __init__(self, chain_for_id=None, int_for_id=None, name=None, organization=None):
        '''
        Constructor
        '''

        self.name = name
        self.organization = organization
        self.datasets = []
        self._chain_for_id = chain_for_id
        self._int_for_id = int_for_id
        self.source_id = self._generate_id()


    def _generate_id(self):
        return "sou_" + self._chain_for_id + "_" + str(self._int_for_id)


    def add_dataset(self, dataset):
        self.datasets.append(dataset)
        dataset.source = self