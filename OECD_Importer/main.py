"""
Created on 09/01/2014

@author: Miguel Otero
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), 'CountryReconciler'))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), "LandPortalEntities"))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), "ModelToXml"))


import logging
import ConfigParser
from es.weso.oecdextractor.rest.rest_client import RestClient
from es.weso.oecdextractor.translator.oecd_translator import OecdTranslator


def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='oecd_extractor.log', level=logging.INFO, 
                        format=FORMAT)


def run():
    configure_log()
    logger = logging.getLogger('main')
    logger.info('Starting run')

    config_path = './es/weso/oecdextractor/configuration/data_sources.ini'
    config = ConfigParser.ConfigParser()
    config.read(config_path)
    try:
        try:
            extractor = RestClient(logger, config)
            extractor.run()
        except BaseException as e:
            logger.error("While trying to download data from teh source: " + e.message)
            raise RuntimeError()

        try:
            translator = OecdTranslator(logger, config, config.getboolean("TRANSLATOR", "historical_mode"))
            translator.run()

        except BaseException as e:
            logger.error("While trying to introduce raw info into our model: " + e.message)
            raise RuntimeError

    finally:
        with open(config_path, 'wb') as configfile:
            config.write(configfile)



if __name__ == '__main__':
    try:
        run()
        print "Done!"
    except:
        print "Execution finalized with errors. Check log."
