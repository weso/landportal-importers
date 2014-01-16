'''
Created on 14/01/2014

@author: Dani
'''
import logging
import urllib2
import xlrd
import sys
from ConfigParser import ConfigParser

class IpfriExtractor(object):
    '''
    classdocs
    '''

    def __init__(self):
        self.log = logging.getLogger('ipfriextractor')
        self.configure_properties()
        self.read_years()
        self.read_url_pattern()
        '''
        Constructor
        '''
    '''
    This method put a properties file in self.config
    '''    
    def configure_properties(self):
        self.config = ConfigParser()
        self.config.read("../../../files/configuration.ini")
    
    '''
    This method put a list of available years in self.years 
    '''
    def read_years(self):
        #line_years should be a group of years separated by ","
        line_years = self.config.get("IPFRI", "available_years")
        self.years =  line_years.split(",")
    
    '''
    This method put a string in self.url_pattern, containing a URL
    in wich we should substitute "{year}" by a concrete year to
    dowload data of a certain date
    '''
    def read_url_pattern(self):
        self.url_pattern = self.config.get("IPFRI", "url_pattern")
        
    '''
    This method download all the info from IPFRI
    '''
    def run(self):
        self.log.info("Initializing data extraction from IPFRI...")
        for year in self.years:
            self.download_year_data(year)
        self.log.info("Data extraction from IPFRI ended")
    
    '''
    This method download info from a single year
    '''
    def download_year_data(self, year):
        try:
            valid_url = self.url_pattern.replace("{year}", str(year))
            self.log.info("Tracking data from {0} ...".format(valid_url))
            #The second parameter in the next function is the final path of the downloaded file
            #self.downloading_action(valid_url, "TestXLS" + str(year) + ".xlsx")
            response = urllib2.urlopen(valid_url)
            xls_content = response.read()
            self.write_binary_to_file(xls_content, "TestXLS" + str(year) + ".xlsx")
            self.log.info("Tracking data from {0} ended.".format(valid_url))
            
        except:
            e = sys.exc_info()[0]
            self.log.exception("Unable to download info from {0}. Data of that year will be ignored. Cause: {1}".format(str(year), e))
        
        
    '''
    In this case, it looks like dowloading using urlretrieve or 
    similar methods of the urllib2 retrieve a corrupt file. However,
    reading it byte by byte, it works
    '''
    def downloading_action(self, valid_url, file_name):
        content = urllib2.urlopen(valid_url) 
        tamano_archivo = int(content.info().getheaders("Content-Length")[0]) / 1024 #size in kbs
        byte = 0
        print 'eeeeee'
        xls_file = open(file_name, 'wb') 
        while (byte != tamano_archivo): 
                xls_file.write(content.read(byte)) 
                byte += 1 
                #sys.stdout.write('\r[*]Descargados:  %8s Kbs de %s Kbs' % (byte, tamano_archivo)) 
        xls_file.close()
        try:
            doc = xlrd.open_workbook(file_name)
            print doc.nsheets
            
        except:
            print 'No abre, ves?'
    
    def write_binary_to_file(self, text, file_name):
        fileStream = open(str(file_name), "wb")
        fileStream.write(text)
        fileStream.close()
        
        
        