'''
Created on 13/01/2014

@author: Miguel Otero
'''

class Region(object):
    '''
    classdocs
    '''


    def __init__(self, name, is_part_of):
        '''
        Constructor
        '''
        self.name = name
        self.is_part_of = is_part_of
        
    def __eq__(self, other):
        return self.name == other.name
