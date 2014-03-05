'''
Created on 14/01/2014

@author: Dani
'''
import logging
from es.weso.extractor.IpfriExtractor import IpfriExtractor
from es.weso.translator.ipfri_trasnlator import IpfriTranslator

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wbextractor.log', level=logging.INFO, 
                        format=FORMAT)

def run():
    configure_log()
    # xml_extractor = IpfriExtractor()
    # xml_extractor.run()
    xml_translator = IpfriTranslator("InforXLSX_2013.xlsx")
    xml_translator.run()
    print 'Done!'


if __name__ == '__main__':
    run()