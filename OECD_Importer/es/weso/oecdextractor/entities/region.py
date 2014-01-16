'''
Created on 13/01/2014

@author: Miguel Otero
'''

class Region(object):
    '''
    classdocs
    '''


    def __init__(self, name, code, order):
        '''
        Constructor
        '''
        self.name = name
        self.code = code
        self.order = order
        
    def __eq__(self, other):
        return self.code == other.code
