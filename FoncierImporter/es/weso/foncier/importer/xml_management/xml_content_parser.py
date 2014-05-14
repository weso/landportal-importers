__author__ = 'Dani'

try:
    import xml.etree.cElementTree as ETree
except:
    import xml.etree.ElementTree as ETree

from ..entities.xml_register import XmlRegister


class XmlContentParser(object):
    #
    # year=year,
    #           month=month,
    #              bornages=self._look_for_field(tree, self.BORNAGES),
    #            csj=self._look_for_field(tree, self.CSJ),
    #             mutations=self._look_for_field(tree, self.MUTATIONS),
    #               titres_crees=self._look_for_field(tree, self.TITRES_CREES),
    #               reperages=self._look_for_field(tree, self.REPERAGES),
    #     reproduction_des_plants=self._look_for_field(tree, self.REP_DES_PLANS)

    BORNAGES = ".//iTopBornagesEff"
    CSJ = ".//iDomCvjDel"
    MUTATIONS = ".//iDomMutationsEff"
    TITRES_CREES = ".//iDomTitreCrees"
    REPERAGES = ".//iTopReperagesEff"
    REP_DES_PLANS = ".//iTopReproductionPlans"

    VALUE = "value"


    def __init__(self, log):
        self._log = log

    def turn_xml_into_register(self, year, month, xml_content):
        tree = ETree.fromstring(xml_content)

        result = XmlRegister(year=year,
                             month=month,
                             bornages=self._look_for_field(tree, self.BORNAGES),
                             csj=self._look_for_field(tree, self.CSJ),
                             mutations=self._look_for_field(tree, self.MUTATIONS),
                             titres_crees=self._look_for_field(tree, self.TITRES_CREES),
                             reperages=self._look_for_field(tree, self.REPERAGES),
                             reproduction_des_plans=self._look_for_field(tree, self.REP_DES_PLANS)
                             )
        return result

    def _look_for_field(self, tree, field_to_look_for):
        base_node = tree.find(field_to_look_for)
        return base_node.find(self.VALUE).text



