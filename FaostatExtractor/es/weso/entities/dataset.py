'''
Created on 02/02/2014

@author: Miguel Otero
'''

class Dataset(object):
    '''
    classdocs
    '''


    def __init__(self, frequency, source):
        '''
        Constructor
        '''
        self.frequency = frequency
        self.source = source
        self.slices = []
    
    def add_slice(self, data_slice):
        self.slices.append(data_slice)
        data_slice.dataset = self
        