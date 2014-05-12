'''
Created on 02/02/2014

@author: Miguel Otero
'''

class Computation(object):

    RAW = "Raw"
    ESTIMATED = "Estimated"  # TODO: Ask Labra about the proper content ot this
    CALCULATED = "Calculated"  # TODO: Ask Labra about the proper content of this

    '''
    classdocs
    '''

    def __init__(self, uri=None):
        '''
        Constructor
        '''
        self.uri = uri