__author__ = 'Dani'


class KeyMapper(object):


    SIGI_KEY = "S"
    SIGI_RANK_KEY = "SR"
    FAMILY_CODE_KEY = "FC"
    FAMILY_CODE_RANK_KEY = "FCR"
    CIVIL_KEY = "C"
    CIVIL_RANK_KEY = "CR"
    ENTITLEMENTS_KEY = "E"
    ENTITLEMENTS_RANK_KEY = "ER"

    LAND_KEY = "L"
    INHERITANCE_GENERAL_KEY = "IG"
    INHERITANCE_DAUGHTERS_KEY = "ID"
    INHERITANCE_WIDOWS_KEY = "IW"

    #################

    _GID2_ID = "GID2"

    _GID2_SIGI_KEY = "SIGI_VAL"
    _GID2_SIGI_RANK_KEY = "SIGI_RANK"
    _GID2_FAMILY_CODE_KEY = "FC_VALUE"
    _GID2_FAMILY_CODE_RANK_KEY = "FC_RANK"
    _GID2_CIVIL_KEY = "CIVIL_VALUE"
    _GID2_CIVIL_RANK_KEY = "CIVIL_RANK"
    _GID2_ENTITLEMENTS_KEY = "OWR_VALUE"
    _GID2_ENTITLEMENTS_RANK_KEY = "OWR_RANK"

    _GID2_LAND_KEY = "OWR_1"
    _GID2_INHERITANCE_GENERAL_KEY = "FC_2"
    # _GID2_INHERITANCE_DAUGHTERS_KEY = "ID"   Does not exist in GID2
    # _GID2_INHERITANCE_WIDOWS_KEY = "IW"

    ##########

    _GIDDB_2012_ID = "GIDDB2012"

    _GIDDB2012_SIGI_KEY = "SIGI_VALUE"
    _GIDDB2012_SIGI_RANK_KEY = "SIGI_RANK"
    _GIDDB2012_FAMILY_CODE_KEY = "FC_VALUE"
    _GIDDB2012_FAMILY_CODE_RANK_KEY = "FC_RANK"
    _GIDDB2012_CIVIL_KEY = "CIVL_VALUE"
    _GIDDB2012_CIVIL_RANK_KEY = "CIVL_RANK"
    _GIDDB2012_ENTITLEMENTS_KEY = "RR_VALUE"
    _GIDDB2012_ENTITLEMENTS_RANK_KEY = "RR_RANK"

    _GIDDB2012_LAND_KEY = "RR_1"
    _GIDDB2012_INHERITANCE_GENERAL_KEY = "FC_4"
    _GIDDB2012_INHERITANCE_DAUGHTERS_KEY = "FC_4_1"
    _GIDDB2012_INHERITANCE_WIDOWS_KEY = "FC_4_2"

    _key_dict = {}

    @staticmethod
    def map_key(key, dataset_id):
        if len(KeyMapper._key_dict) == 0:
            KeyMapper._build_key_dict()
        return KeyMapper._key_dict[dataset_id][key]

    @staticmethod
    def identify_dataset(dataset_url):
        if KeyMapper._GID2_ID in dataset_url:
            return KeyMapper._GID2_ID
        elif KeyMapper._GIDDB_2012_ID in dataset_url:
            return KeyMapper._GIDDB_2012_ID
        else:
            raise RuntimeError("Dataset unrecognized. Imposibble to map indicator keys")

    @staticmethod
    def _build_key_dict():
        #GID2
        gid2_dict = {KeyMapper._GID2_SIGI_KEY: KeyMapper.SIGI_KEY,
                     KeyMapper._GID2_SIGI_RANK_KEY: KeyMapper.SIGI_RANK_KEY,
                     KeyMapper._GID2_FAMILY_CODE_KEY: KeyMapper.FAMILY_CODE_KEY,
                     KeyMapper._GID2_FAMILY_CODE_RANK_KEY: KeyMapper.FAMILY_CODE_RANK_KEY,
                     KeyMapper._GID2_CIVIL_KEY: KeyMapper.CIVIL_KEY,
                     KeyMapper._GID2_CIVIL_RANK_KEY: KeyMapper.CIVIL_RANK_KEY,
                     KeyMapper._GID2_ENTITLEMENTS_KEY: KeyMapper.ENTITLEMENTS_KEY,
                     KeyMapper._GID2_ENTITLEMENTS_RANK_KEY: KeyMapper.ENTITLEMENTS_RANK_KEY,
                     KeyMapper._GID2_LAND_KEY: KeyMapper.LAND_KEY,
                     KeyMapper._GID2_INHERITANCE_GENERAL_KEY: KeyMapper.INHERITANCE_GENERAL_KEY}

        giddb2012 = {KeyMapper._GIDDB2012_SIGI_KEY: KeyMapper.SIGI_KEY,
                     KeyMapper._GIDDB2012_SIGI_RANK_KEY: KeyMapper.SIGI_RANK_KEY,
                     KeyMapper._GIDDB2012_FAMILY_CODE_KEY: KeyMapper.FAMILY_CODE_KEY,
                     KeyMapper._GIDDB2012_FAMILY_CODE_RANK_KEY: KeyMapper.FAMILY_CODE_RANK_KEY,
                     KeyMapper._GIDDB2012_CIVIL_KEY: KeyMapper.CIVIL_KEY,
                     KeyMapper._GIDDB2012_CIVIL_RANK_KEY: KeyMapper.CIVIL_RANK_KEY,
                     KeyMapper._GIDDB2012_ENTITLEMENTS_KEY: KeyMapper.ENTITLEMENTS_KEY,
                     KeyMapper._GIDDB2012_ENTITLEMENTS_RANK_KEY: KeyMapper.ENTITLEMENTS_RANK_KEY,
                     KeyMapper._GIDDB2012_LAND_KEY: KeyMapper.LAND_KEY,
                     KeyMapper._GIDDB2012_INHERITANCE_GENERAL_KEY: KeyMapper.INHERITANCE_GENERAL_KEY,
                     KeyMapper._GIDDB2012_INHERITANCE_DAUGHTERS_KEY: KeyMapper.INHERITANCE_DAUGHTERS_KEY,
                     KeyMapper._GIDDB2012_INHERITANCE_WIDOWS_KEY: KeyMapper.INHERITANCE_WIDOWS_KEY}

        KeyMapper._key_dict[KeyMapper._GID2_ID] = gid2_dict
        KeyMapper._key_dict[KeyMapper._GIDDB_2012_ID] = giddb2012

