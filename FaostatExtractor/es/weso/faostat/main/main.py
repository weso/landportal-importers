'''
Created on 15/01/2014

@author: Dani
'''

import logging
from es.weso.faostat.extractor.faostat_extractor import FaostatExtractor
from es.weso.faostat.translator.faostat_translator import FaostatTranslator
from ConfigParser import ConfigParser


def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='faostat.log', level=logging.INFO, 
                        format=FORMAT)


def run(look_for_historical=True):
    config = ConfigParser()
    config.read("../../../../files/configuration.ini")
    log = logging.getLogger('faostatlog')

    configure_log()
    csv_extractor = FaostatExtractor(log, config)
    csv_extractor.run()
    # csv_indicatorcatcher = FaostatIndicatorCatcher()
    # csv_indicatorcatcher.run()
    csv_translator = FaostatTranslator(log, config, look_for_historical)
    csv_translator.run()

    
    print 'Done!'


if __name__ == '__main__':
    run(True)