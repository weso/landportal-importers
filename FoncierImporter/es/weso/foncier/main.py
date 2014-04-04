__author__ = 'Dani'


import logging
from ConfigParser import ConfigParser

from .importer.foncier_importer import FoncierImporter

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='foncierextractor.log', level=logging.INFO,
                        format=FORMAT)

def run():
    configure_log()
    log = logging.getLogger("foncierextractor")
    config = ConfigParser()
    config.read("../../files/configuration.ini")

    foncierImporter = FoncierImporter(log, config)
    foncierImporter.run()

    print "Done!"

if __name__ == '__main__':
    run()
