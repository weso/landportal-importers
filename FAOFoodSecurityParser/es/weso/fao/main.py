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
    
    try:
        config_path = "../../../files/configuration.ini"
        config = ConfigParser()
        config.read(config_path)
    
        fao_importer = FaoImporter(log, config, config.getboolean("TRANSLATOR", "historical_mode"))
        fao_importer.run()
        update_ini_file(fao_importer, config, config_path)
    except Exception as detail:
        log.error("OOPS! Something went wrong: %s" %detail)
        
    log.info("Done!")

def update_ini_file(importer, config, config_path):
    print "Updating ini file"
    config.set("TRANSLATOR", 'obs_int', importer._obs_int)
    config.set("TRANSLATOR", 'sli_int', importer._sli_int)
    config.set("TRANSLATOR", 'dat_int', importer._dat_int)
    config.set("TRANSLATOR", 'igr_int', importer._igr_int)
    with open(config_path, 'wb') as configfile:
        config.write(configfile)
 
if __name__ == '__main__':
    run()
