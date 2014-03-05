'''
Created on 02/02/2014

@author: Miguel Otero
'''

class Computation(object):

    RAW = "purl.org/weso/ontology/computex#raw"
    ESTIMATED = "purl.org/weso/ontology/computex#estimated"
    '''
    classdocs
    '''

    def __init__(self, uri = None):
        '''
        Constructor
        '''
        self.uri = uri