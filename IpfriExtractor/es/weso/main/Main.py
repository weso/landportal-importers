'''
Created on 14/01/2014

@author: Dani
'''
import logging
from es.weso.extractor.IpfriExtractor import IpfriExtractor

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wbextractor.log', level=logging.INFO, 
                        format=FORMAT)

def run():
    configure_log()
    xml_extractor = IpfriExtractor()
    xml_extractor.run()
    print 'Done!'


if __name__ == '__main__':
    run()