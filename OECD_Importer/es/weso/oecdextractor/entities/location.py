'''
Created on 13/01/2014

@author: Miguel Otero
'''

class Location(object):
    '''
    classdocs
    '''


    def __init__(self, name, iso3_code, parent_member_code, order, metadata):
        '''
        Constructor
        '''
        self.name = name
        self.iso3_code = iso3_code
        self.parent_member_code = parent_member_code
        self.order = order
        self.metadata = metadata
        
    def __eq__(self, other):
        return self.iso3_code == other.iso3_code
    