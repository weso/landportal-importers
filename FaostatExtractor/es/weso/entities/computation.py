'''
Created on 02/02/2014

@author: Miguel Otero
'''

class Computation(object):
    '''
    classdocs
    '''
    RAW = 0
    NORMALIZED = 1
    CALCULED = 2
    


    def __init__(self, computation_type):
        '''
        Constructor
        '''
        self.computation_type = computation_type
        