'''
Created on Apr 21, 2014

@author: Borja
'''

import os.path

import xlrd

from data import __data__


class XslReader(object):
    
    def __init__(self):
        if not os.path.exists(__data__.path()):
            os.makedirs(__data__.path())
            
        self._data_path = __data__.path();
        
        
    def load_xsl(self, file_name, sheet_name):
        inpath = os.path.join(self._data_path, os.path.basename(file_name))
        
        workbook = xlrd.open_workbook(inpath)
        worksheet = workbook.sheet_by_name(sheet_name)
        
        #print worksheet.ncols
        #print worksheet.nrows
        
        data_matrix = [[0 for x in xrange(worksheet.ncols-1)] for x in xrange(worksheet.nrows-1)]
        
        for curr_row in range (0, worksheet.nrows-1):
            for curr_col in range (0, worksheet.ncols-1):
                #print "%s,%s   ---- %s" %(curr_row, curr_col, worksheet.cell_value(curr_row, curr_col))
                if worksheet.cell_type(curr_row, curr_col) == 1:  # text cell
                    data_matrix[curr_row][curr_col] = worksheet.cell_value(curr_row, curr_col).encode("UTF-8");
                else:
                    data_matrix[curr_row][curr_col] = worksheet.cell_value(curr_row, curr_col);
                     
        return data_matrix
