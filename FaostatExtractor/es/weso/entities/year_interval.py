'''
Created on 27/01/2014

@author: Miguel Otero
'''

from es.weso.oecdextractor.entities.interval import Interval

class YearInterval(Interval):
    '''
    classdocs
    '''


    def __init__(self, year):
        '''
        Constructor
        '''
        self.year = year