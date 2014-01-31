'''
Created on 15/01/2014

@author: Dani
'''

import logging
from es.weso.faostat.extractor.faostat_extractor import FaostatExtractor
from es.weso.faostat.indicator_catcher.faostat_indicator_catcher import FaostatIndicatorCatcher
from es.weso.faostat.translator.faostat_translator import FaostatTranslator

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='faostat.log', level=logging.INFO, 
                        format=FORMAT)


def run():

    configure_log()
#     csv_extractor = FaostatExtractor()
#     csv_extractor.run()
#    csv_indicatorcatcher = FaostatIndicatorCatcher()
#    csv_indicatorcatcher.run()
    csv_translator = FaostatTranslator()
    csv_translator.run(True)  
    
    
    
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