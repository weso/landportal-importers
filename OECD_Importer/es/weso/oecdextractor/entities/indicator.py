'''
Created on 13/01/2014

@author: Miguel Otero
'''

class Indicator(object):
    '''
    classdocs
    '''


    def __init__(self, name, description, is_part_of):
        '''
        Constructor
        '''
        self.name = name
        self.description = description
        self.is_part_of = is_part_of
        
    def __eq__(self, other):
        return self.name == other.name
    