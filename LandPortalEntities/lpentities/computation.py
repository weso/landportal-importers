'''
Created on 02/02/2014

@author: Miguel Otero
'''

class Computation(object):

    RAW = "purl.org/weso/ontology/computex#raw"
    '''
    classdocs
    '''

    def __init__(self, uri = None):
        '''
        Constructor
        '''
        self.uri = uri