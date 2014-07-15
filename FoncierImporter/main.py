__author__ = 'Dani'

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), 'CountryReconciler'))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), "LandPortalEntities"))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), "ModelToXml"))

import logging
from ConfigParser import ConfigParser

from es.weso.foncier.importer.foncier_importer import FoncierImporter

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='foncierextractor.log', level=logging.INFO,
                        format=FORMAT)

def run():
    configure_log()
    log = logging.getLogger("foncierextractor")
    config = ConfigParser()
    config.read("./files/configuration.ini")

    try:
        foncier_importer = FoncierImporter(log, config, config.getboolean("TRANSLATOR", "historical_mode"))
        foncier_importer.run()
        log.info("Data successfully downloaded and incorpored to the system.")
    except BaseException as e:
        log.error("While trying to import data: " + e.message)
        raise RuntimeError()



if __name__ == '__main__':
    try:
        run()
        print "Done!"
    except:
        print "Execution finalized with errors. Check log."
