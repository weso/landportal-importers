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
            
        self._data_path = __data__.path()
        
        
    def load_xsl(self, file_name, rows_range, cols_range):
        inpath = os.path.join(self._data_path, os.path.basename(file_name))
        
        workbook = xlrd.open_workbook(inpath)
        worksheet = workbook.sheet_by_index(0)
        
        first_row = int(rows_range[0])
        first_col = int(cols_range[0])
        rows_number = int(rows_range[1]) - int(rows_range[0]) + 1
        cols_number = int(cols_range[1]) - int(cols_range[0]) + 1
        
        data_matrix = [[0 for x in xrange(cols_number)] for x in xrange(rows_number)]
        for curr_row in range (int(rows_range[0]), int(rows_range[1]) + 1):
            for curr_cell in range (int(cols_range[0]), int(cols_range[1]) + 1):
                if worksheet.cell_type(curr_row, curr_cell) == 1:  # text cell
                    data_matrix[curr_row - first_row][curr_cell - first_col] = worksheet.cell_value(curr_row, curr_cell).encode("UTF-8");
                else:
                    data_matrix[curr_row - first_row][curr_cell - first_col] = worksheet.cell_value(curr_row, curr_cell);
        
        return data_matrix
        
