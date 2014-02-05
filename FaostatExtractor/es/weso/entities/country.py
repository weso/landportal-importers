'''
Created on 18/12/2013

@author: Nacho
'''

from es.weso.entities.region import Region

class Country(Region):
    '''
    classdocs
    '''


    def __init__(self, name, is_part_of, fao_uri, iso2, iso3):
        '''
        Constructor
        '''
        super(Country, self).__init__(name, is_part_of)
        self.fao_uri = fao_uri
        self.iso2 = iso2
        self.iso3 = iso3
        