'''
Created on 18/12/2013

@author: Nacho
'''

class Observation(object):
    '''
    classdocs
    '''


    def __init__(self, year, indicator, value, country):
        '''
        Constructor
        '''
        self.year = year
        self.indicator = indicator
        self.value = value
        self.country = country
        