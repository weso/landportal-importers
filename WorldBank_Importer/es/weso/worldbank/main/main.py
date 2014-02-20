"""
Created on 18/12/2013

@author: Nacho
"""
import logging

from es.weso.worldbank.parser.parser import Parser


def configure_log():
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='wbimporter.log', level=logging.WARNING,
                        format=log_format)

def run():
    configure_log()
    parser = Parser()
    parser.extract_countries()
    parser.extract_observations(True, '2007')
    parser.model_to_xml()


if __name__ == '__main__':
    run()
