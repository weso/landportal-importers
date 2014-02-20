'''
Created on 10/02/2014

@author: Dani
'''
import logging
from ConfigParser import ConfigParser
from es.weso.countryrec.parser.file_parser import FileParser 
class CountryReconciler(object):
    '''
    classdocs
    '''


    def __init__(self):
        self.config = ConfigParser()
        self.config.read("../conf/configuration.ini")
        self.log = logging.getLogger("countryRec.log")
        self.clist = FileParser(self.config, self.log).run()
        '''
        Constructor
        '''
        