'''
Created on 10/02/2014

@author: Dani
'''


import xlrd
from es.weso.countryrec.entities.parsed_country import ParsedCountry
from es.weso.countryrec.normalizer.country_name_normalizer import CountryNameNormalizer
class FileParser(object):
    '''
    classdocs
    '''
    #ROW INDEX
    SELF_GOVERNING_FIRST = 1
    SELF_GOVERNING_LAST = 198
    NON_SELF_GOVERNING_FIRST = 200
    NON_SELF_GOVERNING_LAST = 225
    OTHERS_FIRST = 227
    OTHERS_LAST = 227
    
    #COLUMN INDEX
    
    URI_COL = 1
    NAME_EN_COL = 17
    NAME_ES_COL = 19
    NAME_FR_COL = 18
    ISO2_COL = 3
    ISO3_COL = 2
    FAOSTAT_COD_COL = 6
    UNDP_COD_COL = 5
    GAUL_COD_COL = 7
    FAOTERM_COD_COL = 8
    AGROVOC_COD_COL = 9
    UN_COD_COL = 4
    
     
    
    

    def __init__(self, config, log):
        self.config = config
        self.log = log
        self.source_file = config.get("SOURCE", "path_file")
        self.clist = [] #Will contain all the country objects
    
    def run(self):
        self.parse_file()
        return self.clist
    
    def parse_file(self):
        book = xlrd.open_workbook(self.source_file).sheet_by_index(0)
        self.parse_self_governing(book)
        self.parse_non_self_governing(book)
        self.parse_others(book)
#         book = xlrd.open_workbook("country_list.xlsx")
#         print "The number of worksheets is", book.nsheets
#         print "Worksheet name(s):", book.sheet_names()
#         sh = book.sheet_by_index(0)
#         print sh.name, sh.nrows, sh.ncols
#         print "Cell (2,0) is: ", sh.cell_value(rowx=2, colx=0)
#         for rx in range(8):
#             print sh.row(rx)
#         pass
    def parse_self_governing(self, book):
        self.parse_row_range(book, self.SELF_GOVERNING_FIRST, self.SELF_GOVERNING_LAST+1)
    
    def parse_non_self_governing(self, book):
        self.parse_row_range(book, self.NON_SELF_GOVERNING_FIRST, self.NON_SELF_GOVERNING_LAST+1)
    
    def parse_others(self, book):
        self.parse_row_range(book, self.OTHERS_FIRST, self.OTHERS_LAST+1)
    
    def parse_row_range(self, book, first, last):
        for row in range(first, last):
            country = ParsedCountry()
            country.uri = self.parse_some_string(book, row, self.URI_COL)
            country.name_es = self.parse_name_es(book, row)
            country.name_en = self.parse_name_en(book, row)
            country.name_fr = self.parse_name_fr(book, row)
            country.iso2 = self.parse_some_string(book, row, self.ISO2_COL)
            country.iso3 = self.parse_some_string(book, row, self.ISO3_COL)
            country.undp_cod = self.parse_some_string(book, row, self.UNDP_COD_COL)
            country.faostat_cod = self.parse_some_code(book, row, self.FAOSTAT_COD_COL)
            country.gaul_cod = self.parse_some_code(book, row, self.GAUL_COD_COL)
            country.faoterm_cod = self.parse_some_code(book, row, self.FAOTERM_COD_COL)
            country.agrovoc_cod = self.parse_some_code(book, row, self.AGROVOC_COD_COL)
            country.un_cod = self.parse_some_code(book, row, self.UN_COD_COL)
            
            self.clist.append(country)
            # print "{0} in row {1}".format(country.name_es,row+1)         
    
    def whiteValue(self, value):
        if value == None or str(value).strip() == "":
            return True
        return False
    
    def parse_some_string(self, book, row, col):
        value = book.row(row)[col].value
        if self.whiteValue(value):
            print "White string in row {0}, columna {1}".format(row, col)
            return None  
        return str(value).strip()
    
    def parse_name_es(self, book, row):
        value = book.row(row)[self.NAME_ES_COL].value
        if self.whiteValue(value):
            return None
        return CountryNameNormalizer.normalize_es_country(value)
    
    def parse_name_en(self, book, row):
        value = book.row(row)[self.NAME_EN_COL].value
        if self.whiteValue(value):
            return None
        return CountryNameNormalizer.normalize_en_country(value)
    
    def parse_name_fr(self, book, row):
        value = book.row(row)[self.NAME_FR_COL].value
        if self.whiteValue(value):
            return None
        return CountryNameNormalizer.normalize_fr_country(value)
    
    def parse_some_code(self, book, row, col):
        value = book.row(row)[col].value
        if self.whiteValue(value):
            print "white int in row{0}, columna {1}".format(row+1, col)
            return None
        return int(value)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            
            
        
        
        