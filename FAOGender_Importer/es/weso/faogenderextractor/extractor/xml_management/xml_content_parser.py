__author__ = 'Dani'

try:
    import xml.etree.cElementTree as ETree
except:
    import xml.etree.ElementTree as ETree


from ...entities.xml_entities import XmlRegister, IndicatorData
from lpentities.year_interval import YearInterval
from lpentities.interval import Interval
from ..keys_dict import KeysDict


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
        """
        It returns an XmlRegister object or None if the response does not contain usefull info

        """
        tree = None
        try:
            tree = ETree.fromstring(response)
            print "SUPE HACER UNO!"

        except:
            #TODO. Beeter info here
            print "Something is going wrong"
            return None

        return self._turn_tree_into_xml_register(tree)


    def _turn_tree_into_xml_register(self, tree):
        if self._is_empty_tree(tree):
                return None
        country = self._get_country_of_tree(tree)
        result = XmlRegister(country=country)

        try:


            #The next two local variables will be needed in the for loop.
            base_node_in_wich_to_look_for = tree.find("lang").find("topics").find("topic")  # Exploring the tree
            codes_to_look_for = [KeysDict.TOTAL_HOLDERS_CODE,
                                 KeysDict.WOMEN_HOLDERS_CODE,
                                 KeysDict.HOLDINGS_CO_OWNERSHIP_CODE,
                                 KeysDict.RURAL_HOUSEHOLDS_WOMEN_CODE]
            for code in codes_to_look_for:
                data_of_an_indicator = self._look_for_indicator_data(base_node_in_wich_to_look_for, code)
                if not data_of_an_indicator is None:
                    result.add_indicator_data(data_of_an_indicator)

            return result
        except BaseException as e:
            print "_______________LAAAA LIAMOS con", country.iso3, e.message
            return None


    def _look_for_indicator_data(self, base_node, code):
        """
        Return an IndicatorData object if it finds usefull info. If not, return None

        """
        for node in base_node.getchildren():
            if node.attrib["code"] == code:
                return self._get_data_from_a_given_indicator_node(node, code)
        return None


    def _get_data_from_a_given_indicator_node(self, node, code):
        node_value = self._look_for_node_value(node.text)
        node_date = self._look_for_node_date(node.text)

        if not (node_value is None or node_date is None):
            print "Aqui hay algo que merece la pena: ", node_value, node_date.get_time_string()
            return IndicatorData(indicator_code=code,
                                 value=node_value,
                                 date=node_date)
        else:
            #TODO: Maybe make some noise in the log
            return None

    def _look_for_node_value(self, text):
        result = self._remove_text_between_certain_sequences(text, "(", ")")
        result = self._remove_text_between_certain_sequences(result, "[", "]")
        result = self._remove_text_between_certain_sequences(result, "&lt;", "&gt;")
        result = self._remove_text_between_certain_sequences(result, "&", ";")
        result = self._remove_text_between_certain_sequences(result, "<", ">")  # They should be encoded...
        result = result.replace(" ", "")
        return result


    @staticmethod
    def _remove_text_between_certain_sequences(text, beg, end):
        # return text[text.index]
        result = text
        pos_beg = text.find(beg)
        pos_end = text.find(end)
        while not (pos_beg == -1 or pos_end == -1):
            result = result[:result.index(beg)] + result[result.index(end) + len(end):]
            pos_beg = result.find(beg)
            pos_end = result.find(end)
        return result


    @staticmethod
    def _look_for_node_date(text):
        """
        It returns an lpentities Interval if ot finds an intervalic date or a YearInterval object if
        it find a single value. In case of not finding any valid date, returns None

        Asumptions:
         - Dates appear betwen "[]"
         - Only dates (no other data) appear between "[]"
         - There only one date per node

        """

        try:
            string_date = text[text.index('[') + 1:text.index(']')]
        except ValueError:
            print "Aqui hay un string chunguele:", text
            return None
        if "-" in string_date:  # Interval (two values)
            years = string_date.split("-")
            return Interval(start_time=int(years[0]),
                            end_time=int(years[1]))
        else:  # YearInterval (single value)
            return YearInterval(year=int(string_date))



    def _get_country_of_tree(self, tree):
        iso3 = tree.attrib[self.ISO3_ATTR]
        return self._reconciler.get_country_by_iso3(iso3)


    @staticmethod
    def _is_empty_tree(tree):
        """
        Empty means taht it hasn't got available data

        """
        if len(tree.getchildren()) == 0:
            return True
        else:
            return False
        pass

