import ConfigParser
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), "CountryReconciler"))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), "LandPortalEntities"))
sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), "ModelToXml"))

from es.weso.worldbank.parser.parser import Parser

__author__ = 'BorjaGB'

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wbextractor.log', level=logging.INFO,
                        format=FORMAT)

def update_ini_file(config, config_path, importer, log):
    log.info("Updating ini file")
    config.set("TRANSLATOR", 'obs_int', importer._obs_int)
    config.set("TRANSLATOR", 'sli_int', importer._sli_int)
    config.set("TRANSLATOR", 'dat_int', importer._dat_int)
    config.set("TRANSLATOR", 'igr_int', importer._igr_int)
    
    if hasattr(importer, '_historical_year'):
        config.set("TRANSLATOR", 'historical_year', importer._historical_year)
    with open("config_path", 'wb') as configfile:
        config.write(configfile)
                
def run():
    configure_log()
    log = logging.getLogger("wbextractor")
    config_path = "es/weso/worldbank/configuration/api_access.ini"
    config = ConfigParser.RawConfigParser()
    config.read(config_path)

    try:
        wb_importer = Parser(config, log)
        wb_importer.run()
        update_ini_file(config, config_path, wb_importer, log)
        
        log.info("Done!")
    
    except Exception as detail:
        log.error("OOPS! Something went wrong %s" %detail)
        

if __name__ == '__main__':
    run()
