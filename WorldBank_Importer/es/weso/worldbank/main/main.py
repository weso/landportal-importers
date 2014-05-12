"""
Created on 18/12/2013

@author: Nacho
"""

from ConfigParser import ConfigParser
import logging

from es.weso.worldbank.parser.parser import Parser


def configure_log():
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wbimporter.log', level=logging.WARNING,
                        format=log_format)

def run():
    configure_log()
    log = logging.getLogger("es.weso.worldbank.parser.parser")
    
    config_path = '../configuration/api_access.ini'
    config = ConfigParser()
    config.read(config_path)

    try:
        parser = Parser(config, log)
        parser.extract_countries()
        parser.extract_observations(True, '2007')
        parser.model_to_xml()
        update_ini_file(parser, config, config_path)
    except Exception as detail:
        log.error("OOPS! Something went wrong: %s" %detail)
        
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
