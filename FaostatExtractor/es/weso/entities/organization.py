'''
Created on 02/02/2014

@author: Miguel Otero
'''

class Organization(object):
    '''
    classdocs
    '''


    def __init__(self, name, is_part_of = None):
        '''
        Constructor
        '''
        self.name = name
        self.is_part_of = is_part_of