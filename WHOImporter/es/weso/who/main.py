


import ConfigParser
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
    config = ConfigParser.RawConfigParser()
    config.read("../../../files/configuration.ini")

    who_importer = WhoImporter(log, config, config.getboolean("TRANSLATOR", "historical_mode"))
    who_importer.run()

    print "Updating ini file"
    config.set("TRANSLATOR", 'obs_int', who_importer._obs_int)
    config.set("TRANSLATOR", 'sli_int', who_importer._sli_int)
    config.set("TRANSLATOR", 'dat_int', who_importer._dat_int)
    config.set("TRANSLATOR", 'igr_int', who_importer._igr_int)
    config.set("TRANSLATOR", 'historical_year', who_importer._last_year)
    with open("../../../files/configuration.ini", 'wb') as configfile:
        config.write(configfile)
            
    print "Done!"

if __name__ == '__main__':
    run()
