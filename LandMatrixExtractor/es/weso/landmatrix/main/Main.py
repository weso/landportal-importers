'''
Created on 13/01/2014

@author: Dani
'''
from ConfigParser import ConfigParser

import logging
from es.weso.landmatrix.extractor.LandMatrixExtractorXML import LandMatrixExtractorXML
from es.weso.landmatrix.translator.land_matrix_translator import LandMatrixTranslator

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='land_matrix_extractor.log', level=logging.INFO, 
                        format=FORMAT)

def run():
    configure_log()
    log = logging.getLogger("lmextractor")
    config = ConfigParser()
    config.read("../../../../files/configuration.ini")
    # xml_extractor = LandMatrixExtractorXML()
    # xml_extractor.run()
    translator = LandMatrixTranslator(log, config)
    translator.run(True)
    print 'Done!'

if __name__ == '__main__':
    run()