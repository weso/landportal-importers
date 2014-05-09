"""
Created on 09/01/2014

@author: Miguel Otero
"""

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

    config_path = '../configuration/data_sources.ini'
    config = ConfigParser.ConfigParser()
    config.read(config_path)

    extractor = RestClient(logger, config)
    extractor.run()
    try:
        translator = OecdTranslator(logger, config, True)
        translator.run()
        print "Done!"

    except BaseException as e:
        print e.message

    finally:
        with open(config_path, 'wb') as configfile:
            config.write(configfile)



if __name__ == '__main__':
    run()
