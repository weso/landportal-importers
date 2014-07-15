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
        
        
    def load_xsl(self, indicator_dict, file_name):
        inpath = os.path.join(self._data_path, os.path.basename(file_name))
        
        workbook = xlrd.open_workbook(inpath)
        try:
            worksheet = workbook.sheet_by_index(int(indicator_dict['sheet'])-1)
        except:
            worksheet = workbook.sheet_by_name(indicator_dict['sheet'])
        
        rows = indicator_dict['rows'].split('-')
        columns = indicator_dict['columns'].split('-')
        
        data_matrix = [[0 for x in xrange(int(columns[1])-int(columns[0]))] for x in xrange(int(rows[1])-int(rows[0]))]
        
        for curr_row in range (int(rows[0]), int(rows[1])):
            for curr_col in range (int(columns[0]), int(columns[1])):
                try:
                    #print "%s,%s   ---- %s" %(curr_row, curr_col, worksheet.cell_value(curr_row, curr_col))
                    if worksheet.cell_type(curr_row, curr_col) == 1:  # text cell
                        data_matrix[curr_row-int(rows[0])][curr_col-int(columns[0])] = worksheet.cell_value(curr_row, curr_col).encode("UTF-8");
                    else:
                        data_matrix[curr_row-int(rows[0])][curr_col-int(columns[0])] = worksheet.cell_value(curr_row, curr_col);
                except:
                    print "Error processing the cell [%d,%d]" %(curr_row, curr_col)     
        return data_matrix
