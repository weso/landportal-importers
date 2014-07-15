"""
Created on 18/12/2013

@author: Nacho
"""

import requests
from requests.adapters import HTTPAdapter


class RestClient(object):
        
    @staticmethod
    def get(uri, params):
        s = requests.Session()
        s.mount(uri, HTTPAdapter(max_retries=10))
        json_response = requests.get(uri, params=params).json()
        return json_response