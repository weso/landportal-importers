__author__ = 'Dani'

from model2xml.model2xml import ModelToXMLTransformer

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
        datasets, user, import_process, relations = ModelObjectBuilder(self._log, self._config, json_objects).run()

        for dataset in datasets:
            ModelToXMLTransformer(dataset=dataset,
                                  user=user,
                                  import_process=import_process,
                                  indicator_relations=relations).run()
