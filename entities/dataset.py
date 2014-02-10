'''
Created on 02/02/2014

@author: Miguel Otero
'''

class Dataset(object):
    '''
    classdocs
    '''


    def __init__(self, dataset_id = None, name = None, frequency = None, source = None):
        '''
        Constructor
        '''
        self.dataset_id = dataset_id
        self.name = name
        self.frequency = frequency
        self.source = source
        self.slices = []
        
    def add_slice(self, data_slice):
        self.slices.append(data_slice)
        data_slice.dataset = self