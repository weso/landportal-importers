'''
Created on 09/01/2014

@author: Miguel Otero
'''

import logging
from es.weso.oecdextractor.rest.rest_client import RestClient

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='oecd_extractor.log', level=logging.INFO, 
                        format=FORMAT)

def run():
    configure_log()
    logger = logging.getLogger('main')
    logger.info('Starting run')
    extractor = RestClient()
    extractor.run()

if __name__ == '__main__':
    run()
