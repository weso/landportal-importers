__author__ = 'Dani'

import requests


class CountriesXmlExtractor(object):

    def __init__(self, log, config, reconciler):

        self._log = log
        self._config = config
        self._reconciler = reconciler

        self._query_pattern = self._config.get("API", "request_pattern")
        self._replace_by_iso = self._config.get("API", "text_to_replace")


    def run(self):
        """
        It returns a list of strings containing xml trees that represents the available info of every country
        available in the reconciler

        """
        result = []
        for a_country in self._reconciler.get_all_countries():
            result.append(self._get_xml_of_a_country(a_country))

        ## This comented code is usefull for fast test. It asks only for 15 countries to the API
        #
        # tris = self._reconciler.get_all_countries()
        # for i in range(0, 15):
        #     result.append((self._get_xml_of_a_country(tris[i])))

        return result


    def _get_xml_of_a_country(self, country):
        string_request = self._query_pattern.replace(self._replace_by_iso, country.iso3)
        self._log.info("Tracking data from " + country.iso3 + "...")
        return requests.get(string_request).content




