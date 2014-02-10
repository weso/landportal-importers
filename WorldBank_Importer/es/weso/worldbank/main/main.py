'''
Created on 18/12/2013

@author: Nacho
'''
import logging

from es.weso.worldbank.parser.parser import Parser


def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wbimporter.log', level=logging.INFO, 
                        format=FORMAT)

def run():
    configure_log()
    parser = Parser()
    parser.extract_countries()
    parser.extract_observations(True, '2007')

if __name__ == '__main__':
    run()
