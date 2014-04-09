__author__ = 'Dani'

from ..entities.deal import Deal


class DealsBuilder(object):

    def __init__(self):
        pass

    @staticmethod
    def turn_node_into_deal_object(info_node):
        """
        It receives a node (Element of ElementTree) and returns a deal object containing the needed data

        """
        a_deal = Deal()
        a_deal.target_country = _extract_target_country(info_node)
        a_deal.date = _extract_date(info_node)
        a_deal.hectares = _extract_hectares(info_node)
        a_deal.sectors = _extract_sectors(info_node)

        return a_deal


#############################################################################################
#                                       FUNCTIONS                                           #
#############################################################################################

###  Contants

PROPERTY = "name"
TARGET_COUNTRY = "target_country"
SECTROS = "intention"
NO_VALUE = "None"



#Functions


def _extract_target_country(info_node):
    for subnode in info_node.getchildren():
        if subnode[PROPERTY] == TARGET_COUNTRY:
            return subnode.text
    raise_error("country", "not found")


def _extract_date(info_node):
    #TODO: no idea yet of what to consider date
    return "a"


def _extract_hectares(info_node):
    #TODO: no idea yet of what to consider valid hectares
    return "a"


def _extract_sectors(info_node):
    #Looking for text
    text = None
    for subnode in info_node.getchildren():
        if subnode[PROPERTY] == TARGET_COUNTRY:
            text = subnode.text
            break
    if text is None or text == NO_VALUE:
        raise_error("sectors", "not found")
        return  # It will throw an error, the next won't execute.... but let's ensure that
    result = []
    candidate_sectors = text.split(",")
    for candidate in candidate_sectors:
        if not (candidate is None or candidate == ""):
            result.append(candidate.replace(" ", ""))
    if len(result) == 0:
        raise_error("sectors", "not found")
    return result



def raise_error(concrete_filed, cause):
    raise RuntimeError("Error while parsing {0} in a node. Cause: {1}. Node will be ignored".format(concrete_filed,
                                                                                                    cause))

