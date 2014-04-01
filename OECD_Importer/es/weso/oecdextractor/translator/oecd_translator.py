__author__ = 'Dani'

from .json_loader import JsonLoader
from .model_object_builder import ModelObjectBuilder

class OecdTranslator(object):

    def __init__(self, log, config):
        self._log = log
        self._config = config
        pass


    def run(self):
        """
        Steps:
         - Load json content from file
         - Turn json into model objects
         - Send model to model2xml

        """
        json_objects = JsonLoader(self._log, self._config).run()
        datasets = ModelObjectBuilder(self._log, self._config, json_objects).run()

        pass
