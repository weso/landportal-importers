'''
Created on 18/12/2013

@author: Nacho
'''
import logging

import requests
from requests.adapters import HTTPAdapter

class RestClient(object):
    '''
    classdocs
    '''

    def __init__(self):
        self.logger = logging.getLogger("es.weso.worldbank.rest.rest_client")
        
    def get(self, uri, params):
        self.logger.info("Performing a get request from {0} " + 
                         "with following parameters {1}".format(uri, params))
        s = requests.Session()
        s.mount(uri, HTTPAdapter(max_retries=10))
        json_response = requests.get(uri, params=params).json()
        return json_response
    