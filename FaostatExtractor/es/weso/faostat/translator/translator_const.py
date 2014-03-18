'''
Created on 03/02/2014

@author: Dani
'''

class TranslatorConst(object):
    '''
    This class is only used to provide some constants handy for many class of the package

    '''
    COUNTRY_CODE = 0
    COUNTRY = 1
    ITEM_CODE = 2
    ITEM = 3
    ELEMENT_GROUP = 4
    ELEMENT_CODE = 5
    ELEMENT = 6
    YEAR = 7
    UNIT = 8
    VALUE = 9
    FLAG = 10
    COMPUTATION_PROCESS = 11  # Non-parsed field
    EXPECTED_NUMBER_OF_COLS = 11  # All the fields but the non-parsed COMPUTATION_PROCESS
    

    CODE_LAND_AREA = 6601
    CODE_AGRICULTURAL_LAND = 6610
    CODE_FOREST_LAND = 6661
    CODE_ARABLE_LAND = 6621

    #  The next three are random numbers that are not it the previous indicator codes.
    CODE_RELATIVE_AGRICULTURAL_LAND = 999888777
    CODE_RELATIVE_ARABLE_LAND = 999888776
    CODE_RELATIVE_FOREST_LAND = 999888775
    

        