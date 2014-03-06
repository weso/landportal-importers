"""
Created on 10/02/2014

@author: Dani
"""

from lpentities.country import Country

class ParsedCountry(object):

    def __init__(self, iso3_official=None, iso3_fao=None, iso2=None,
                 sname_en=None, sname_es=None, sname_fr=None,
                 un_code=None, faostat_code=None):
        """
        In case that we find a data source that uses other identifier for countries, we
        have to add it as a parameter of this constructor in order to match it with its
        corresponding country. Also, it will be necessary to implement the normalizer
        and reconciler methods. A reconciler method will only be needed if the new
        identifier is a slightly variable value such as the country name. Note that this
        identifier must be in country_list Excel file!
        """
        self.iso3_official = iso3_official
        self.iso3_fao = iso3_fao
        self.iso2 = iso2
        self.sname_en = sname_en
        self.sname_es = sname_es
        self.sname_fr = sname_fr
        self.un_code = un_code
        self.faostat_code = faostat_code

        self.model_object = Country(iso3=self.get_iso3(), name=self.sname_en, iso2=self.iso2)

    def get_iso3(self):
        # This is a small validation for missing or malformed official ISO3 values
        # In that cases we'll use the FAO ISO3 code
        if self.iso3_official is not None and len(self.iso3_official) == 3:
            return self.iso3_official
        else:
            return self.iso3_fao  # If this is None, we are doomed