'''
Created on 31/01/2014

@author: Dani
'''
from .translator_const import TranslatorConst
from lpentities.computation import Computation

class RelativeRegistersCalculator(object):
    '''
    classdocs
    '''


    def __init__(self, log, imported_registers, land_dictionary, key_generation_function):
        """
        Constructor

        """
        self.imported_registers = imported_registers
        self.land_dictionary = land_dictionary
        self.key_generation_function = key_generation_function
        self._log = log



        
    def run(self):
        calculated_registers = []

        for imported in self.imported_registers:
            if self._need_to_calculate_a_relative_register(imported):
                try:
                    calculated_registers.append(self._calculate_relative_register(imported))
                except BaseException as e:
                    self._log.warning("Exception while calculating relative register, observation ignored: " + e.message)
        return calculated_registers

    def _calculate_relative_register(self, imported):
        relative = []

        relative.insert(TranslatorConst.COUNTRY_CODE, self._infer_country_code(imported))
        relative.insert(TranslatorConst.COUNTRY, self._infer_country(imported))
        relative.insert(TranslatorConst.ITEM_CODE, self._infer_item_code(imported))
        relative.insert(TranslatorConst.ITEM, self._infer_item(imported))
        relative.insert(TranslatorConst.ELEMENT_GROUP, self._infer_element_group(imported))
        relative.insert(TranslatorConst.ELEMENT_CODE, self._infer_element_code(imported))
        relative.insert(TranslatorConst.ELEMENT, self._infer_element(imported))
        relative.insert(TranslatorConst.YEAR, self._infer_year(imported))
        relative.insert(TranslatorConst.UNIT, self._infer_unit())  # Always the same, no parameter needed
        relative.insert(TranslatorConst.VALUE, self._infer_value(imported))
        relative.insert(TranslatorConst.FLAG, self._infer_flag(imported))
        relative.insert(TranslatorConst.COMPUTATION_PROCESS, self._infer_computation_type()) #Always the same



        return relative

    @staticmethod
    def _infer_computation_type():
        return Computation.CALCULATED

    @staticmethod
    def _infer_flag(imported):
        return imported[TranslatorConst.FLAG]

    def _infer_value(self, imported):
        key_land = self.key_generation_function(country_code=imported[TranslatorConst.COUNTRY_CODE],
                                                year=imported[TranslatorConst.YEAR])
        try:

            land_area = self.land_dictionary[key_land]
            return 100 * float(imported[TranslatorConst.VALUE]) / float(land_area)
        except BaseException as e:
            raise RuntimeError("Error while infering relative value of an observation. Country {0}. Cause: {1}."
                               .format(key_land, e.message))

    @staticmethod
    def _infer_unit():
        return "%"

    @staticmethod
    def _infer_year(imported):
        return imported[TranslatorConst.YEAR]

    @staticmethod
    def _infer_element(imported):
        return imported[TranslatorConst.ELEMENT]

    @staticmethod
    def _infer_element_code(imported):
        return imported[TranslatorConst.ELEMENT_CODE]

    @staticmethod
    def _infer_element_group(imported):
        return imported[TranslatorConst.ELEMENT_GROUP]

    @staticmethod
    def _infer_item(imported):

        imported_code = imported[TranslatorConst.ITEM_CODE]
        if imported_code == TranslatorConst.CODE_FOREST_LAND:
            return "Relative forest land"
        elif imported_code == TranslatorConst.CODE_AGRICULTURAL_LAND:
            return "Relative agricultural land"
        elif imported_code == TranslatorConst.CODE_ARABLE_LAND:
            return "Return relative agricultural land"
        else:
            raise RuntimeError("Unrecognised item code while generating calculated registers: {0}.".
                                                                                            format(imported_code))
    @staticmethod
    def _infer_item_code(imported):

        imported_code = imported[TranslatorConst.ITEM_CODE]
        if imported_code == TranslatorConst.CODE_FOREST_LAND:
            return TranslatorConst.CODE_RELATIVE_FOREST_LAND
        elif imported_code == TranslatorConst.CODE_AGRICULTURAL_LAND:
            return TranslatorConst.CODE_RELATIVE_AGRICULTURAL_LAND
        elif imported_code == TranslatorConst.CODE_ARABLE_LAND:
            return TranslatorConst.CODE_RELATIVE_ARABLE_LAND
        else:
            raise RuntimeError("Unrecognised item code while generating calculated registers: {0}.".
                                                                                            format(imported_code))

    @staticmethod
    def _infer_country(imported):
        return imported[TranslatorConst.COUNTRY]

    @staticmethod
    def _infer_country_code(imported):
        return imported[TranslatorConst.COUNTRY_CODE]

    @staticmethod
    def _need_to_calculate_a_relative_register(imported):
        """
        We must calculate a relative register always but when we are managing an observation referred to Land Area
        That info is precisely the used one to make the rest of relative calculations

        """
        if imported[TranslatorConst.ITEM_CODE] == TranslatorConst.CODE_LAND_AREA:
            return False
        return True
