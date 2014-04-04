'''
Created on 18/12/2013

@author: Nacho
'''

from .region import Region

class Country(Region):
    '''
    classdocs
    '''


    def __init__(self, name=None, is_part_of=None, iso2=None, iso3=None, un_code=None):
        '''
        Constructor
        '''
        super(Country, self).__init__(name=name, is_part_of=is_part_of, un_code=un_code)
        self.iso2 = iso2
        self.iso3 = iso3
        
    def get_dimension_string(self):
        return self.iso3