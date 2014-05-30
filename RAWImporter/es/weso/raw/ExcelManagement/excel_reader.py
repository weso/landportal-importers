'''
Created on Apr 21, 2014

@author: Borja
'''

import os.path

import xlrd

import __data__


class XslReader(object):
    
    def __init__(self):
        if not os.path.exists(__data__.path()):
            os.makedirs(__data__.path())
            
        self._data_path = __data__.path();
        
    def load_indicator_sheet(self, file_name):
        inpath = os.path.join(self._data_path, os.path.basename(file_name))
        
        workbook = xlrd.open_workbook(inpath)
        worksheet = workbook.sheet_by_name("Indicators")
        
        data_dictionary = {}
        
        for curr_col in range (0, worksheet.ncols):
            field_name = worksheet.cell_value(0, curr_col).decode("UTF-8")
            data_dictionary[field_name] = worksheet.cell_value(1, curr_col);
                
        return data_dictionary
                    
    def load_organization_sheet(self, file_name):
        inpath = os.path.join(self._data_path, os.path.basename(file_name))
        
        workbook = xlrd.open_workbook(inpath)
        worksheet = workbook.sheet_by_name("Organization")
        
        data_dictionary = {}
        
        data_dictionary["Name"] = worksheet.cell_value(1, 1).decode("UTF-8")
        data_dictionary["Description_EN"] = worksheet.cell_value(2, 1).decode("UTF-8")
        data_dictionary["Description_ES"] = worksheet.cell_value(3, 1).decode("UTF-8")
        data_dictionary["Description_FR"] = worksheet.cell_value(4, 1).decode("UTF-8")
        data_dictionary["URL"] = worksheet.cell_value(5, 1).decode("UTF-8")
        data_dictionary["Logo"] = worksheet.cell_value(6, 1).decode("UTF-8")
        
        data_dictionary["License_Name"] = worksheet.cell_value(9, 1).decode("UTF-8")
        data_dictionary["License_Description"] = worksheet.cell_value(10, 1).decode("UTF-8")
        data_dictionary["License_Republish"] = worksheet.cell_value(11, 1)
        data_dictionary["License_URL"] = worksheet.cell_value(12, 1).decode("UTF-8")
        
        return data_dictionary
    
    def load_xsl(self, file_name):
        inpath = os.path.join(self._data_path, os.path.basename(file_name))
        
        workbook = xlrd.open_workbook(inpath)
        worksheet = workbook.sheet_by_name("Values")
        
        data_matrix = [[0 for x in xrange(worksheet.ncols)] for x in xrange(worksheet.nrows)]
        
        for curr_row in range (0, worksheet.nrows):
            for curr_col in range (0, worksheet.ncols):
                #print "%s,%s   ---- %s" %(curr_row, curr_col, worksheet.cell_value(curr_row, curr_col))
                if worksheet.cell_type(curr_row, curr_col) == 1:  # text cell
                    data_matrix[curr_row][curr_col] = worksheet.cell_value(curr_row, curr_col).encode("UTF-8");
                else:
                    data_matrix[curr_row][curr_col] = worksheet.cell_value(curr_row, curr_col);
                     
        return data_matrix
