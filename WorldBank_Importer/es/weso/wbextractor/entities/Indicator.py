'''
Created on 19/12/2013

@author: Nacho
'''

class Indicator(object):
    '''
    classdocs
    '''


    def __init__(self, indicator_id, name, source_notes, source_organization):
        '''
        Constructor
        '''
        self.indicator_id = indicator_id
        self.name = name
        self.source_notes = source_notes
        self.source_organization = source_organization
        