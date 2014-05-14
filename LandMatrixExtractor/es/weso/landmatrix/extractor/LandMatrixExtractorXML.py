'''
Created on 13/01/2014

@author: Dani
'''

import urllib2
import logging
import sys
from ConfigParser import ConfigParser
from es.weso.util.file_writer import FileWriter


class LandMatrixExtractorXML(object):
    
    '''
    classdocs
    '''


    def __init__(self, log, config):
        """
        Constructor
        """

        self._config = config
        self._log = log

    def run(self):
        """
        Downloads the entire Land Matrix database

        """
        try:
            self._log.info('Running Land matrix xml extractor...')
            response = urllib2.urlopen(self._config.get("LAND_MATRIX", "url_download"))
            xml_content = response.read()
            FileWriter.write_text_to_file(xml_content, self._config.get("LAND_MATRIX", "target_file"))
            self._log.info('Land matrix xml extractor finished')
        except BaseException as e:
            raise RuntimeError("Unable to track data from {0}... Cause: {1}"
                               .format(self._config.get("LAND_MATRIX", "url_download"), e.message))


