'''
Created on 15/01/2014

@author: Dani
'''
import sys
import urllib2
import logging
from zipfile import ZipFile
from ConfigParser import ConfigParser
from es.weso.util.file_writer import FileWriter
class FaostatExtractor(object):
    '''
    classdocs
    '''


    def __init__(self):
        self.config = ConfigParser()
        self.config.read("../../../files/configuration.ini")
        self.log = logging.getLogger('faostatlog')
        '''
        Constructor
        '''
        
        pass
    
    '''
    This method dowload the entire data base of faostat in csv format.
    The estructure of the scv is as follows:
    CountryCode(int),Country(string),ItemCode(int),Item(string),ElementGroup(int),
    ElementCode(int),Element(string),Year(int),Unit(string),Value(float),Flag(char)
    '''
    def run(self):
        self.log.info("Starting process...")
        try:
            zip_file_name = self.download_zip_file()
            self.extract_zip_file(zip_file_name)
            self.log.info("Proccess succesfully ended")
        except RuntimeError, (strerror):
            self.log.error(strerror)
            print strerror
            print "Estoy cascando"
    '''
    Extracts the content of a zip file in the path zip_file_name and put it
    content in the place specified by the configuration parameter ["FAOSTAT", "datapath"] 
    '''
    def extract_zip_file(self, zip_file_name):
        self.log.info("Extracting data from zip file...")
        sourceZip = ZipFile(zip_file_name) #open the zip File
        if len(sourceZip.namelist()) != 1: #The zip file should contain a single element
            raise RuntimeError("Unexpected zip file. Content will not be extracted")
        else:
            sourceZip.extract(sourceZip.namelist()[0], self.config.get("FAOSTAT", "data_file_path"))
            self.log.info("Data extracted to {0}".format(self.config.get("FAOSTAT", "data_file_path")))

        
    '''
    Returns the name of a zip file containing the entire faostat database
    '''
    def download_zip_file(self):
        try:
            self.log.info("Downloading data from {0}".format(self.config.get("FAOSTAT", "zip_url")))
            response = urllib2.urlopen(self.config.get("FAOSTAT", "zip_url"))
            zip_content = response.read()
            self.log.info("Data downloaded. Writing to disk...")
            target_file = self.config.get("FAOSTAT", "zip_file_path")
            FileWriter. write_binary_to_file(zip_content, target_file)
            self.log.info("Data written in disk")
            return target_file
        except:
            e = sys.exc_info()[0]
            raise RuntimeError("Unable to save data from {0}. Cause: {1}".format(self.config.get("FAOSTAT", "zip_url"), e))
            
    
    
    
    
    
    