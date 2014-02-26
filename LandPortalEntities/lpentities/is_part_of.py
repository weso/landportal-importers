'''
Created on 02/02/2014

@author: Miguel Otero
'''

from .indicator_relationship import IndicatorRelationship

class IsPartOf(IndicatorRelationship):
    '''
    classdocs
    '''


    def __init__(self, source = None, target = None):
        '''
        Constructor
        '''
        super(IsPartOf, self).__init__(source, target)