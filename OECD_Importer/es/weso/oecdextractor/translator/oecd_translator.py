__author__ = 'Dani'

from model2xml.model2xml import ModelToXMLTransformer

from .model_object_builder import ModelObjectBuilder


class OecdTranslator(object):

    def __init__(self, log, config, look_for_historical=True):
        self._log = log
        self._config = config
        self._look_for_historical = look_for_historical
        pass


    def run(self):
        """
        Steps:
         - Turn json into model objects
         - Send model to model2xml

        """
        object_builder = ModelObjectBuilder(log=self._log,
                                            config=self._config,
                                            look_for_historical=self._look_for_historical)
        dataset_file_pair, user, relations = object_builder.run()

        errors_count = 0
        for a_pair in dataset_file_pair:
            try:
                ModelToXMLTransformer(dataset=a_pair.other_object,
                                      user=user,
                                      import_process=ModelToXMLTransformer.JSON,
                                      indicator_relations=relations,
                                      path_to_original_file=a_pair.file_path).run()
            except BaseException as e:
                self._log.error(e.message)
                errors_count += 1
        if errors_count < len(dataset_file_pair):  # If some observation could reach the server, we have to actualize ids
            object_builder.actualize_config_values()
        if errors_count > 0:
            raise RuntimeError("Errors whie generating data from 1 or more datasets.")
        self._log.info("Data has been successfully incropored to the system.")  # It will only execute if there were no errors
