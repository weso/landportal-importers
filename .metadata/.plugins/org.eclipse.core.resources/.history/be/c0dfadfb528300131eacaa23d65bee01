'''
Created on 21/01/2014

@author: Miguel Otero
'''

import logging
from es.weso.faogenderextractor.fileaccess.file_access import FileAccess

class FaoGenderExtractor(object):
    '''
    classdocs
    '''
    
    logger = logging.getLogger('faogender_extractor')
    file_access= FileAccess()

    def __init__(self):
        '''
        Constructor
        '''
        self.countries = []
        
    def extract_countries(self):
        self.file_access.obtain_countries()
    
    