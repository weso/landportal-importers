'''
Created on 21/01/2014

@author: Dani
'''

from ConfigParser import ConfigParser
from es.weso.util.file_writer import FileWriter
import os

class FaostatIndicatorCatcher(object):
    '''
    classdocs
    '''


    def __init__(self):
        self.config = ConfigParser()
        self.config.read("../../../../files/configuration.ini")
        '''
        Constructor
        '''
        pass
    
    def run(self):
        wlist = self.read_csv_file_fields()
        indicators_info = self.prepare_indicators_info(wlist)
        FileWriter.write_text_to_file(indicators_info, self.config.get("INDICATOR_CATCHER", "result_file_path"))
        
    def prepare_indicators_info(self, wlist):
        result = "List of available indicators:\n"
        for word in wlist:
            result += "\n\t" + word
        return result
    
    def read_csv_file_fields(self):
        wlist = []
        csv_file = os.listdir(self.config.get("FAOSTAT", "data_file_path"))[0]
        if csv_file[-4:] != '.csv':
            raise RuntimeError("Unexpected content while looking for indicators. CSV file expected but {0} was found".format(csv_file))
        
        
        content = open(self.config.get("FAOSTAT", "data_file_path") + "/" + csv_file).readlines()
        for i in range(1,len(content)):
            line = content[i].split(",\"")
            interesting_word = line[3];
            self.treat_interesting_word(wlist, interesting_word)
        return wlist

    def treat_interesting_word(self, wlist, word):
        if not word in wlist:
            wlist.append(word)
            print word  # Comment?
            
    