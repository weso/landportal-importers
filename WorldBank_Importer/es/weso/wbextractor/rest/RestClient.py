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
    logger = logging.getLogger("es.weso.wbextractor.rest.RestClient")

    def __init__(self, base_uri):
        '''
        Constructor
        '''
        self.base_uri = base_uri
        
    def build_uri(self, relative_uri):
        uri = self.base_uri + relative_uri
        return uri
        
    def get(self, relative_uri, params):
        uri = self.build_uri(relative_uri)
        self.logger.info("Performing a get request from {0} with following parameters {1}".format(uri, params))
        s = requests.Session()
        s.mount(uri, HTTPAdapter(max_retries=10))
        resp_json = requests.get(uri, params=params).json()
        return resp_json                
    
    def post(self, relative_uri, params):
        pass
    
    def get_base_uri(self):
        return self.base_uri