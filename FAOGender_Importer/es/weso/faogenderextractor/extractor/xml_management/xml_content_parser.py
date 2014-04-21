__author__ = 'Dani'

try:
    import xml.etree.cElementTree as ETree
except:
    import xml.etree.ElementTree as ETree

from ...entities.xml_entities import XmlRegister, IndicatorData


class XmlContentParser(object):

    ISO3_ATTR = "iso3"

    def __init__(self, log, config, reconciler, responses):
        self._log = log
        self._config = config
        self._reconciler = reconciler
        self._responses = responses



    def run(self):
        """
        It rreturns a list of XmlRegister objects containing all the info that

        """

        result = []
        for response in self._responses:
            parsed_response = self._process_response(response)
            if parsed_response is not None:
                result.append(parsed_response)

        return result


    def _process_response(self, response):
        tree = None
        try:
            tree = ETree.fromstring(response)

        except:
            #TODO. Beeter info here
            print "Something is going wrong"
            return None

        return self._turn_tree_into_xml_register(tree)


    def _turn_tree_into_xml_register(self, tree):
        if self._is_empty_tree(tree):
            return None

        result = XmlRegister(country=self._get_country_of_tree(tree))




    def _get_country_of_tree(self, tree):
        iso3 = tree.attr[self.ISO3_ATTR]
        return self._reconciler.get_country_by_iso3(iso3)


    @staticmethod
    def _is_empty_tree(tree):
        """
        Empty means taht it hasn't got available data

        """
        if len(tree.getchildren) == 0:
            return True
        else:
            return False
        pass

