from ConfigParser import ConfigParser
import logging

from es.weso.fao.importer.fao_importer import FaoImporter


__author__ = 'BorjaGB'


def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='faoextractor.log', level=logging.INFO,
                        format=FORMAT)

def run():
    configure_log()
    log = logging.getLogger("faoimporter")
    config = ConfigParser()
    config.read("../../../files/configuration.ini")

    fao_importer = FaoImporter(log, config, config.getboolean("TRANSLATOR", "historical_mode"))
    fao_importer.run()

    print "Done!"

if __name__ == '__main__':
    run()
