# coding=utf-8
"""
Created on 10/02/2014

@author: Dani
"""

from lpentities.country import Country

class ParsedCountry(object):

    def __init__(self, iso3_official=None, iso3_fao=None, iso3_a2=None,
                 iso2=None, sname_en=None, sname_es=None, sname_fr=None,
                 un_code=None, faostat_code=None, lname_en=None,
                 lname_es=None, lname_fr=None, alt_en_name1=None,
                 alt_en_name2=None):
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
        self.iso3_a2 = iso3_a2
        self.iso2 = iso2
        self.sname_en = sname_en
        self.sname_es = sname_es
        self.sname_fr = sname_fr
        self.un_code = un_code
        self.faostat_code = faostat_code

        self.lname_en = lname_en
        self.lname_es = lname_es
        self.lname_fr = lname_fr
        self.alt_en_name1 = alt_en_name1
        self.alt_en_name2 = alt_en_name2

        self.alias = []
        self.model_object = Country(iso3=self.get_iso3(),
                                    name=self._get_valid_en_name(),
                                    iso2=self.get_iso2())


    def get_iso2(self):
        if self.iso2 is None:
            return None
        else:
            return self.iso2.decode('utf-8', 'ignore')

    def get_iso3(self):
        # This is a small validation for missing or malformed official ISO3 values
        # In that cases we'll use the FAO ISO3 code
        if self.iso3_official is not None and len(self.iso3_official) == 3:
            return self.iso3_official.decode('utf-8', 'ignore')
        elif self.iso3_fao is not None and len(self.iso3_fao) == 3:
            return self.iso3_fao.decode('utf-8', 'ignore')
        else:
            return self.iso3_a2.decode('utf-8', 'ignore')  # If this is None, we are doomed

    def _get_valid_en_name(self):
        if self.sname_en is not None:
            return self.sname_en.decode('utf-8', 'ignore')
        elif self.lname_en is not None:
            return self.lname_en.decode('utf-8', 'ignore')
        elif self.alt_en_name1 is not None:
            return self.alt_en_name1.decode('utf-8', 'ignore')
        elif self.alt_en_name2 is not None:
            return self.alt_en_name2.decode('utf-8', 'ignore')
        else:
            return None  # But return something...

    def add_alias(self, alias):
        self.alias.append(alias)