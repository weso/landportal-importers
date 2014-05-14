'''
Created on 10/01/2014

@author: Miguel Otero
'''

import requests

class RestClient(object):
    '''
    classdocs
    '''


    CHAIN_TO_REPLACE_FOR_ID = "{DAT_ID}"


    def __init__(self, log, config):
        '''
        Constructor
        '''
        self._log = log
        self._config = config



    def run(self):
        self._log.info("Initializing process of downloading data...")
        #Tasks:
        # - Cahrgue querys
        # - Get the data through a request
        # - Save it in a json
        # dataset_ids = self._charge_dataset_ids()
        # query_pattern = self._charge_query_pattern()
        try:
            requests_to_do = self._build_url_request()
            self._track_data(requests_to_do)
            self._log.info("The data has been succesfully downloaded.")
        except BaseException as e:
            self._log.error("Unable to download the data from the source.")
            raise e


    def _track_data(self, req_to_do):
        file_id = 1
        for a_req in req_to_do:
            json_response = requests.get(a_req).text
            self._save_to_file(json_response, file_id)
            file_id += 1

    def _save_to_file(self, json_response, file_id):
        base_dir = self._config.get("DATASETS", "base_dir")
        file_name = base_dir + "/oecddataset" + str(file_id) + ".json"
        file_stream = open(str(file_name), "w")
        file_stream.write(str(json_response))
        file_stream.close()


    def _charge_dataset_ids(self):
        raw_ids = self._config.get("DATASETS", "dataset_ids").split(",")
        result = []
        for an_id in raw_ids:
            result.append(an_id.replace(" ", ""))
        return result

    def _charge_query_pattern(self):
        return self._config.get("URLs", "query_pattern")

    def _build_url_request(self):
        return self._config.get("URLs", "querys").split("|")
        # return result




    # def obtain_data(self, dataset_id):
    #     self.logger.info('Obtaining data')
    #     request = requests.get(self.data_url.replace('{DATASETID}',
    #                                                   self.datasets[dataset_id]))
    #     if request.status_code != 200 :
    #         self.logger.error('Error retrieving data from URL')
    #         return None
    #     else:
    #         return request.json()
    #
    # def obtain_members(self, dataset_id):
    #     self.logger.info('Obtaining members')
    #     request = requests.get(self.dimension_members_url.replace('{DATASETID}',
    #                                                                self.datasets[dataset_id]))
    #     if request.status_code != 200:
    #         self.logger.error('Error retrieving members from URL')
    #         return None
    #     else:
    #         return request.json()
            
        