__author__ = 'Dani'

import json
import os
class JsonLoader(object):

    def __init__(self, log, config):
        self._log = log
        self._config = config

    def run(self):
        """
        It must return as many json objects as datasets we have

        """
        result = []
        base_dir = self._config.get("DATASETS", "base_dir")
        candidate_files = os.listdir(base_dir)
        for candidate_file in candidate_files:
            if os.path.splitext(candidate_file)[1] == ".json":
                result.append(self._turn_file_into_json_object(base_dir + "/" + candidate_file))
        return result

    @staticmethod
    def _turn_file_into_json_object(path_to_file):
        json_file = open(path_to_file)
        json_string = json_file.read()
        json_file.close()
        return json.loads(json_string)

        pass

