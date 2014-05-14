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
        config_path = "../../../../files/configuration.ini"
        config.read(config_path)
        log = logging.getLogger('faostatlog')
        configure_log()
        try:
            csv_extractor = FaostatExtractor(log, config)
            csv_extractor.run()
        except BaseException as e:
            log.error("While tracking file: " + e.message)
            raise RuntimeError()

        try:
            csv_translator = FaostatTranslator(log, config, look_for_historical)
            csv_translator.run()
        except BaseException as e:
            log.error("While trying to turn raw info into xml: " + e.message)
            raise RuntimeError()

        with open(config_path, 'w') as configfile:
            config.write(configfile)






if __name__ == '__main__':
    try:
        run(True)
        print "Done!"
    except:
        print "Execution finalized with errors. Check logs."