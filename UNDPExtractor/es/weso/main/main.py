'''
Created on 13/01/2014

@author: Dani
'''
import logging

from es.weso.extractor.undp_extractor import UNDPExtractor
from es.weso.translator.undp_translator import UNDPTranslator

import os.path

def run():
    configure_log()
    xml_extractor = UNDPExtractor("xml")
    xml_extractor.run()
    xml_translator = UNDPTranslator()
    xml_translator.run()
    print 'Done!'

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='UNDP_extractor.log', level=logging.INFO, 
                        format=FORMAT)


if __name__ == '__main__':
    run()