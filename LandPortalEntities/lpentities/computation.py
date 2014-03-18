'''
Created on 02/02/2014

@author: Miguel Otero
'''

class Computation(object):

    RAW = "purl.org/weso/ontology/computex#Raw"
    ESTIMATED = "purl.org/weso/ontology/computex#estimated"  # TODO: Ask Labra about the proper content ot this
    CALCULATED = "purl.org/weso/ontology/computex#calculated"  # TODO: Ask Labra about the proper content of this

    '''
    classdocs
    '''

    def __init__(self, uri=None):
        '''
        Constructor
        '''
        self.uri = uri