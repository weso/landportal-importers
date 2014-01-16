'''
Created on 18/12/2013

@author: Nacho
'''
import logging

from es.weso.wbextractor.WorldBankExtractor import WorldBankExtractor


def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wbextractor.log', level=logging.INFO, 
                        format=FORMAT)

def run():
    configure_log()
    extractor = WorldBankExtractor()
    topic_id = extractor.extract_topic()
    if topic_id != None :
        extractor.extract_indicators_by_topic(topic_id)
        extractor.extract_countries()
        extractor.extract_observations()

if __name__ == '__main__':
    run()
