'''
Created on Apr 15, 2014

@author: Borja
'''

class IndicatorEndpoint(object):
    '''
    classdocs
    '''

    def __init__(self, indicator_code = None, profile = None, countries = None, regions = None, file_name = None):
        '''
        Constructor
        '''
        self.indicator_code = indicator_code
        self.profile = profile
        self.countries = countries
        self.regions = regions
        self.file_name = file_name
