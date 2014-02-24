'''
Created on 02/02/2014

@author: Miguel Otero
'''


class DataSource(object):
    '''
    classdocs
    '''


    def __init__(self, source_id=None, name=None, organization=None):
        '''
        Constructor
        '''
        self.source_id = source_id
        self.name = name
        self.organization = organization
        self.datasets = []

    def add_dataset(self, dataset):
        self.datasets.append(dataset)
        dataset.source = self