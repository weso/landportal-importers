'''
Created on 10/02/2014

@author: Dani
'''

class ParsedCountry(object):
    '''
    classdocs
    '''


    def __init__(self, row_in_file=None, iso3_official=None, iso3_fao=None, \
                   name_official=None, name_fao=None, un_code=None, \
                   un_opt_code=None):
        self.iso3_official = iso3_official
        self.iso3_fao = iso3_fao
        self.name_official = name_official
        self.name_fao = name_fao
        self.un_code = un_code
        self.un_opt_code = un_opt_code
        self.row_in_file = row_in_file

        '''
        Constructor
        '''
        
    def get_iso3(self):
        if not self.iso3_official =="" and not self.iso3_official == None:
            return self.iso3_official
        else:
            return self.iso3_fao
            
    def get_name(self):
        if not self.name_official == "" and not self.name_official == None:
            return self.iso3_official
        else:
            return self.name_fao
        
    def get_un_code(self):
        if not self.un_code == None: #If the code was correctly parsed, there will be an int in un_code. Else, a None
            return self.un_code
        else:
            return self.un_opt_code