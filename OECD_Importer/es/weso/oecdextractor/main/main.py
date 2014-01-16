'''
Created on 09/01/2014

@author: Miguel Otero
'''

import logging
from es.weso.oecdextractor.oecd_extractor import OECDExtractor

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='oecd_extractor.log', level=logging.INFO, 
                        format=FORMAT)

def run():
    configure_log()
    logger = logging.getLogger('main')
    logger.info('Starting run')
    extractor = OECDExtractor()
    extractor.extract_members('dataset_id_09')
    extractor.extract_data('dataset_id_09')
    extractor.extract_members('dataset_id_12')
    extractor.extract_data('dataset_id_12')

if __name__ == '__main__':
    run()
