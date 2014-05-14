__author__ = 'Dani'

try:
    import xml.etree.cElementTree as ETree
except:
    import xml.etree.ElementTree as ETree


from ...entities.xml_entities import XmlRegister, IndicatorData
from lpentities.year_interval import YearInterval
from lpentities.interval import Interval
from ..keys_dict import KeysDict

from datetime import datetime


class XmlContentParser(object):

    ISO3_ATTR = "iso3"

    def __init__(self, log, config, reconciler, responses, look_for_historical):
        self._log = log
        self._config = config
        self._reconciler = reconciler
        self._responses = responses
        self._look_for_historical = look_for_historical



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
        except BaseException as e:
            self._log.warning("Error while parsing a response. The importer will try to process the rest "
                              "of the data. Cause: " + e.message)
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
                if (not data_of_an_indicator is None) and self._pass_filters(data_of_an_indicator):
                    result.add_indicator_data(data_of_an_indicator)

            return result
        except BaseException as e:
            self._log.warning("Unable to track data from country {0}. Country will be ignored. Cause: {1}"
                              .format(country.iso3, e.message))
            return None

    def _pass_filters(self, data_of_an_indicator):
        if self._look_for_historical:
            return True

        if not "_target_date" in self.__dict__:
            self._target_date = self._get_current_date()
        elif self._get_year_of_data_indicator(data_of_an_indicator) < self._target_date:
            return False
        return True

    def _get_current_date(self):
        return int(self._config.get("HISTORICAL", "first_valid_year"))

    @staticmethod
    def _get_year_of_data_indicator(data_of_an_indicator):
        date_obj = data_of_an_indicator.date
        if type(date_obj) == YearInterval:
            return int(date_obj.year)
        elif type(date_obj) == Interval:
            return int(date_obj.end_time)
        else:
            raise RuntimeError("Unexpected object date. Impossible to build observation from it: " + type(date_obj))

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
            return IndicatorData(indicator_code=code,
                                 value=node_value,
                                 date=node_date)
        else:
            return None

    def _look_for_node_value(self, text):
        result = self._remove_text_between_certain_sequences(text, "(", ")")
        result = self._remove_text_between_certain_sequences(result, "[", "]")
        result = self._remove_text_between_certain_sequences(result, "&lt;", "&gt;")
        result = self._remove_text_between_certain_sequences(result, "&", ";")
        result = self._remove_text_between_certain_sequences(result, "<", ">")  # They should be encoded...
        result = result.replace(" ", "")
        result = result.replace(",", "")
        result = result.replace("\n", "")
        result = result.replace("\t", "")
        result = result.replace("\r", "")
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


    def _look_for_node_date(self, text):
        """
        It returns an lpentities Interval if ot finds an intervalic date or a YearInterval object if
        it find a single value. In case of not finding any valid date, returns None

        Asumptions:
         - Dates appear betwen "[]"
         - Sometimes, more things than dates appear between "[]"
         - We have got several date formats: XXXX, XX, XXXX-XXXX, XXXX-XX, XX-XX, XXXX/XXXX, XXXX/XX, XX/XX

        """
        beg_pos = text.find('[')
        end_pos = text.find(']')
        while not (beg_pos == -1 or end_pos == -1):
            string_date = text[beg_pos + 1:end_pos]
            #Trying to return a valid date
            if "-" in string_date:  # Interval (two values)
                years = string_date.split("-")
                return Interval(start_time=self._return_4_digits_year(years[0]),
                                end_time=self._return_4_digits_year(years[1]))
            elif "/" in string_date:
                years = string_date.split("/")
                return Interval(start_time=self._return_4_digits_year(years[0]),
                                end_time=self._return_4_digits_year(years[1]))
            elif "&minus;" in string_date:
                years = string_date.split("&minus;")
                return Interval(start_time=self._return_4_digits_year(years[0]),
                                end_time=self._return_4_digits_year(years[1]))

            elif self._is_single_year(string_date):  # YearInterval (single value)
                return YearInterval(year=int(string_date))

            #Preparing end_pos and beg_pos for potential next iteration
            beg_pos = text.find('[', beg_pos + 1)
            end_pos = text.find(']', end_pos + 1)

        #TODO: maybe make some noise in the log... but probably not. There are so many cases like this
        return None  # We reach this if no fate was found

    @staticmethod
    def _is_single_year(year):
        if year.isdigit():
            try:
                int_year = int(year)
                if 0 < int_year < 100:  # Year of the form 01.02,...,98,99
                    return True
                elif 999 < int_year < 2150:  # Year of 4 digits. In 2150 it will stop working :)
                    return True
                else:  # Unknown year format
                    return False
            except ValueError:
                return False
        else:
            return False


    def _return_4_digits_year(self, year_string):
        if len(year_string) == 4:
            return int(year_string)
        elif len(year_string) == 2:
            final_digits = int(year_string)
            if final_digits < 30:  # So, in 2030, this will stop working.
                return 2000 + final_digits
            else:
                return 1900 + final_digits
        else:
            raise RuntimeError("Date with a number of digits different tahn 2 or 4: " + year_string)

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

