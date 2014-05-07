'''
Created on 13/01/2014

@author: Dani
'''
import logging

from es.weso.extractor.undp_extractor import UNDPExtractor
from es.weso.translator.undp_translator import UNDPTranslator
from ConfigParser import ConfigParser

import os.path

def run(look_for_historical=True):
    configure_log()
    config = ConfigParser()
    config.read("../../../files/configuration.ini")
    log = logging.getLogger("UNDP_extractor")
    xml_extractor = UNDPExtractor(config, log, "xml")
    xml_extractor.run()
    xml_translator = UNDPTranslator(config, log, look_for_historical)
    xml_translator.run()
    print 'Done!'

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='UNDP_extractor.log', level=logging.INFO, 
                        format=FORMAT)


if __name__ == '__main__':
    run(True)