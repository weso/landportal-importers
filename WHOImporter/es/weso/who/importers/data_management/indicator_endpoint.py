'''
Created on Apr 15, 2014

@author: Borja
'''

class IndicatorEndpoint(object):
    '''
    classdocs
    '''

    def __init__(self, code = None, profile = None, countries = None, regions = None, file_name = None):
        '''
        Constructor
        '''
        self.code = code
        self.profile = profile
        self.countries = countries
        self.regions = regions
        self.file_name = file_name
