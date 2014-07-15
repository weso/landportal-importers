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
        self._iso2 = iso2
        self._iso3 = iso3
        
    def __get_iso2(self):
        return self._iso2
    
    def __set_iso2(self, iso2):
        if len(iso2) == 2:
            self._iso2 = iso2
        else:
            raise ValueError("Invalid format for iso2")
        
    iso2 = property(fget=__get_iso2, fset=__set_iso2, doc="ISO2 code of the country")
    
    def __get_iso3(self):
        return self._iso3
    
    def __set_iso3(self, iso3):
        if len(iso3) == 3:
            self._iso3 = iso3
        else:
            raise ValueError("Invalid format for iso3")
        
    iso3 = property(fget=__get_iso3, fset=__set_iso3, doc="ISO3 code of the country")
    
    def get_dimension_string(self):
        return self.iso3