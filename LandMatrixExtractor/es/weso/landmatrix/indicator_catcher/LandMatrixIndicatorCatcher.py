'''
Created on 21/01/2014

@author: Dani
'''

from ConfigParser import ConfigParser
import xml.dom.minidom

class LandMatrixIndicatorCatcher(object):
    '''
    classdocs
    '''


    def __init__(self):
        self.config = ConfigParser
        self.config.read("../../../../files/configuration.ini")
        self.root = xml.dom.minidom.parse(self.config.get("LAND_MATRIX", "target_file"))
        '''
        Constructor
        '''
        
    def run(self):
        #Not implemented yet
        pass
    
        