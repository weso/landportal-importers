'''
Created on 13/01/2014

@author: Dani
'''
import logging

from es.weso.extractor.UNDPExtractor import UNDPExtractor

def run():
    configure_log()
    xml_extractor = UNDPExtractor("xml")
    xml_extractor.run()
    print 'Done!'

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='UNDP_extractor.log', level=logging.INFO, 
                        format=FORMAT)


if __name__ == '__main__':
    run()