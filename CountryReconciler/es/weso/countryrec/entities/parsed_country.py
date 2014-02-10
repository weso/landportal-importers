'''
Created on 10/02/2014

@author: Dani
'''

class ParsedCountry(object):
    '''
    classdocs
    '''


    def __init__(self, uri = None, name_en = None, name_es = None, \
                 name_fr = None, iso2 = None, iso3 = None, faostat_cod = None, \
                 undp_cod = None, gaul_cod = None, faoterm_cod = None, \
                 agrovoc_cod = None, un_cod = None):
        
        self.uri = uri
        self.name_en = name_en
        self.name_es = name_es
        self.name_fr = name_fr
        self.iso2 = iso2
        self.iso3 = iso3
        self.faostat_cod = faostat_cod
        self.undp_cod = undp_cod
        self.gaul_cod = gaul_cod
        self.faoterm_cod = faoterm_cod
        self.agrovoc_cod = agrovoc_cod
        self.un_cod = un_cod
        '''
        Constructor
        '''
        