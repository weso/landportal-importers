'''
Created on 13/01/2014

@author: Dani
'''
from ConfigParser import ConfigParser

import logging
from es.weso.landmatrix.extractor.LandMatrixExtractorXML import LandMatrixExtractorXML
from es.weso.landmatrix.translator.land_matrix_translator import LandMatrixTranslator


def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='land_matrix_extractor.log', level=logging.INFO, 
                        format=FORMAT)


def run(look_for_historical=True):
    configure_log()
    log = logging.getLogger("lmextractor")
    config = ConfigParser()
    config.read("../../../../files/configuration.ini")
    try:
        xml_extractor = LandMatrixExtractorXML(log, config)
        xml_extractor.run()
    except BaseException as ex:
        log.error("While downloading data: " + ex.message)
        raise RuntimeError()

    try:
        translator = LandMatrixTranslator(log, config, look_for_historical=look_for_historical)
        translator.run()
    except BaseException as ex:
        log.error("While trying to incropore raw info into our model: " + ex.message)
        raise RuntimeError()



if __name__ == '__main__':
    try:
        run(True)
        print 'Done!'
    except BaseException as ex:
        print "Execution finalized with errors. Check log."