'''
Created on 21/01/2014

@author: Miguel Otero
'''

import logging
from ConfigParser import ConfigParser

from es.weso.faogenderextractor.extractor.faogender_extractor import FaoGenderExtractor


def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='faogender_extractor.log', level=logging.INFO, 
                        format=FORMAT)

def run():
    configure_log()
    logger = logging.getLogger('main')
    config = ConfigParser()
    config.read("../../../../files/configuration.ini")
    logger.info('Starting run')
    extractor = FaoGenderExtractor(logger, config)
    extractor.run()

if __name__ == '__main__':
    run()