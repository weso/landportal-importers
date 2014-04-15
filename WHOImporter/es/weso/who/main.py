from ConfigParser import ConfigParser
import logging

from es.weso.who.importers.who_importer import WhoImporter


__author__ = 'BorjaGB'


def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='whoextractor.log', level=logging.INFO,
                        format=FORMAT)

def run():
    configure_log()
    log = logging.getLogger("whoextractor")
    config = ConfigParser()
    config.read("../../../files/configuration.ini")

    who_importer = WhoImporter(log, config, True)
    who_importer.run()

    print "Done!"

if __name__ == '__main__':
    run()
