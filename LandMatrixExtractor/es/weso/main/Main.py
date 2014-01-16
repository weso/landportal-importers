'''
Created on 13/01/2014

@author: Dani
'''

import logging
from es.weso.landmatrixextractor.xml.LandMatrixExtractorXML import LandMatrixExtractorXML


def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='land_matrix_extractor.log', level=logging.INFO, 
                        format=FORMAT)

def run():
    configure_log()
    xml_extractor = LandMatrixExtractorXML()
    xml_extractor.run()
    print 'Done!'

if __name__ == '__main__':
    run()