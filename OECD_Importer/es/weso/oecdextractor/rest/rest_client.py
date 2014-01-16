'''
Created on 10/01/2014

@author: Miguel Otero
'''

import requests
import logging
import ConfigParser

class RestClient(object):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('rest_client')
        self.config = ConfigParser.ConfigParser()
        self.config.read('../configuration/data_sources.ini')
        self.data_url = self.config.get('URLs', 'data_url')
        self.dimensions_url = self.config.get('URLs', 'dimensions_url')
        self.dimension_members_url = self.config.get('URLs', 'dimension_members_url')
        self.datasets = dict(self.config.items('DataSets'))
    
    def obtain_data(self, dataset_id):
        self.logger.info('Obtaining data')
        request = requests.get(self.data_url.replace('{DATASETID}',
                                                      self.datasets[dataset_id]))
        if request.status_code != 200 :
            self.logger.error('Error retrieving data from URL')
        else :
            data = request.json()
        return data;
    
    def obtain_members(self, dataset_id):
        self.logger.info('Obtaining members')
        request = requests.get(self.dimension_members_url.replace('{DATASETID}',
                                                                   self.datasets[dataset_id]))
        if request.status_code != 200 :
            self.logger.error('Error retrieving members from URL')
        else :
            data = request.json()
        return data;
            
        