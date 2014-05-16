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
    config.read("./files/configuration.ini")

    try:
        xml_extractor = IpfriExtractor(log, config)
        xml_extractor.run()
    except BaseException as e:
        log.error("While extracting data from the source: " + e.message)
        raise RuntimeError()
    try:
        xml_translator = IpfriTranslator(log, config, True)
        xml_translator.run()
    except BaseException as e:
        log.error("While trying to introduce raw info into our model: " + e.message)
        raise RuntimeError()


if __name__ == '__main__':
    try:
        run()
        print 'Done!'
    except:
        print 'Execution finalized with erros. Check logs'