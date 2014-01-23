'''
Created on 21/01/2014

@author: Miguel Otero
'''

import logging
from es.weso.faogenderextractor.faogender_extractor import FaoGenderExtractor

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='faogender_extractor.log', level=logging.INFO, 
                        format=FORMAT)

def run():
    configure_log()
    logger = logging.getLogger('main')
    logger.info('Starting run')
    extractor = FaoGenderExtractor()
    extractor.extract_countries()

if __name__ == '__main__':
    run()