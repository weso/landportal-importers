__author__ = 'Dani'


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
    config.read("../../../files/configuration.ini")

    try:
        foncier_importer = FoncierImporter(log, config, True)
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
