"""
Created on 13/01/2014

@author: Dani
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), 'CountryReconciler'))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), "LandPortalEntities"))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), "ModelToXml"))


import logging

from es.weso.extractor.undp_extractor import UNDPExtractor
from es.weso.translator.undp_translator import UNDPTranslator
from ConfigParser import ConfigParser



def run():
    configure_log()
    config = ConfigParser()
    config.read("./files/configuration.ini")
    log = logging.getLogger("UNDP_extractor")
    look_for_historical = config.getboolean("TRANSLATOR", "historical_mode")
    try:
        xml_extractor = UNDPExtractor(config, log, "xml")
        xml_extractor.run()
    except BaseException as e:
        log.error("While downloading data from the source: " + e.message)
        raise RuntimeError()

    try:
        xml_translator = UNDPTranslator(config, log, look_for_historical)
        xml_translator.run()
    except BaseException as e:
        log.error("While transforming raw data into our model: " + e.message)
        raise RuntimeError()



def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='UNDP_extractor.log', level=logging.INFO, 
                        format=FORMAT)


if __name__ == '__main__':
    try:
        run()
        print "Done!"
    except:
        print "Execution finalized with errors. Check log."

