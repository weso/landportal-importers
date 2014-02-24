'''
Created on 02/02/2014

@author: Miguel Otero
'''

from es.weso.entities.indicator_relationship import IndicatorRelationship

class Becomes(IndicatorRelationship):
    '''
    classdocs
    '''


    def __init__(self, source = None, target = None):
        '''
        Constructor
        '''
        super(Becomes, self).__init__(source, target)