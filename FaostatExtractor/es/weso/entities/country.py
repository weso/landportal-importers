'''
Created on 13/01/2014

@author: Miguel Otero
'''

from es.weso.oecdextractor.entities.region import Region

class Country(Region):
    '''
    classdocs
    '''


    def __init__(self, fao_uri, iso2_code, iso3_code):
        '''
        Constructor
        '''
        self.fao_uri = fao_uri
        self.iso2_code = iso2_code
        self.iso3_code = iso3_code
        
    def __eq__(self, other):
        return self.iso3_code == other.iso3_code
    