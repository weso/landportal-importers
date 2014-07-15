"""
Created on 21/01/2014

@author: Miguel Otero
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), 'CountryReconciler'))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), "LandPortalEntities"))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), "ModelToXml"))

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
    config.read("./files/configuration.ini")
    logger.info('Starting run')
    try:
        extractor = FaoGenderExtractor(logger, config, config.getboolean("TRANSLATOR", "historical_mode"))
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