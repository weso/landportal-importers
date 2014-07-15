'''
Created on 31/01/2014

@author: Dani
'''

import re
class IndicatorNeededResolver(object):
    '''
    classdocs
    '''


    def __init__(self, config, log):
        self.config = config
        self.log = log
        '''
        Constructor
        '''
    

    def run(self):
        """
        Returns a list of string with the needed indicators

        """
        indicator_needed_filename = self.config.get("TRANSLATOR", "indicator_names_valid_path")
        return self.parse(indicator_needed_filename)
    
    def parse(self, filename):
        file_content = open(filename)
        lines = file_content.readlines()
        file_content.close()
        return self.filter_unusefull_lines(lines)
    
    def filter_unusefull_lines(self, all_lines):
        result = []
        for line in all_lines:
            if line not in ["", "\n", "\r", "\n\r"] and line[0] != "#":
                result.append(re.sub('\n', "", line))
        return result
        
        