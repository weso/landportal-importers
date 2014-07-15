'''
Created on Apr 16, 2014

@author: Borja
'''
import csv
import os.path

from data import __data__


class CsvReader(object):

    def __init__(self):
        if not os.path.exists(__data__.path()):
            os.makedirs(__data__.path())
            
        self._data_path = __data__.path();

    def load_csv(self, file_name):
        inpath = os.path.join(self._data_path, os.path.basename(file_name))
        lines = list()
        
        with open(inpath, 'rb') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                lines.append(row)
        
        return lines.pop(0), lines
        