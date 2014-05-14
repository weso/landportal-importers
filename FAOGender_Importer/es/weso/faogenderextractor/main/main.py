"""
Created on 21/01/2014

@author: Miguel Otero
"""

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
    try:
        extractor = FaoGenderExtractor(logger, config, True)
        extractor.run()
    except BaseException as e:
        logger.error("Error: " + e.message)
        raise RuntimeError()

if __name__ == '__main__':
    try:
        run()
        print "Done!"
    except:
        print "Execution finalized with errors. Check logs."