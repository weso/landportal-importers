'''
Created on 02/02/2014

@author: Miguel Otero
'''

class Computation(object):

    RAW = "computex#Raw"
    ESTIMATED = "computex#Imputed"  # TODO: Ask Labra about the proper content ot this
    CALCULATED = "computex#Computed"  # TODO: Ask Labra about the proper content of this

    '''
    classdocs
    '''

    def __init__(self, uri=None):
        '''
        Constructor
        '''
        self._uri = uri
        
    def __get_uri(self):
        return self._uri
    
    def __set_uri(self, uri):
        if uri == self.RAW or uri == self.ESTIMATED or uri == self.CALCULATED:
            self._uri = uri
        else:
            raise ValueError("Provided uri not in the given values")
        
    uri = property(fget=__get_uri, fset=__set_uri, doc="Kind of uri computation")
    