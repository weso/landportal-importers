'''
Created on 15/01/2014

@author: Dani
'''

import logging
from es.weso.extractor.FaostatExtractor import FaostatExtractor

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='faostat.log', level=logging.INFO, 
                        format=FORMAT)

def run():
    configure_log()
    csv_extractor = FaostatExtractor()
    csv_extractor.run()
    print 'Done!'
    '''
    extractor = WorldBankExtractor()
    topic_id = extractor.extract_topic()
    if topic_id != None :
        extractor.extract_indicators_by_topic(topic_id)
        extractor.extract_countries()
        extractor.extract_observations()
    '''

if __name__ == '__main__':
    run()