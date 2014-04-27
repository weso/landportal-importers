'''
Created on 14/01/2014

@author: Dani
'''
import logging
from ConfigParser import ConfigParser
from es.weso.extractor.IpfriExtractor import IpfriExtractor
from es.weso.translator.ipfri_trasnlator import IpfriTranslator

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wbextractor.log', level=logging.INFO, 
                        format=FORMAT)

def run():
    configure_log()
    log = logging.getLogger('ipfriextractor')
    config = ConfigParser()
    config.read("../../../files/configuration.ini")

    xml_extractor = IpfriExtractor(log, config)
    xml_extractor.run()
    xml_translator = IpfriTranslator(log, config)
    xml_translator.run()
    print 'Done!'


if __name__ == '__main__':
    run()