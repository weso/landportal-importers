# -*- coding: utf-8 -*-

"""
Created on 10/02/2014

@author: Dani
"""

import re
import codecs

from reconciler.entities.normalized_country import NormalizedCountry
from reconciler.exceptions.unknown_country_error import UnknownCountryError


class CountryNormalizer(object):
    """
    In this class we'll implement the normalizer methods responsible
    for returning a NormalizedCountry object from a certain distinctive
    value. If a reconciliation is needed we'll also implement it here.
    """

    # Conflictive expressions
    EN_REMOVABLE_EXPRESSIONS = "(the|in|of|and|&)"
    ES_REMOVABLE_EXPRESSIONS = "(el|las|los|la|lo|de|y|&|del|en)"
    FR_REMOVABLE_EXPRESSIONS = "(les|las|le|la|et|&|dans|de|d|l)"
    A_VOWEL_FORMS = "(Á|À|Â|Ä|á|à|â|ä)"
    E_VOWEL_FORMS = "(É|È|Ê|Ë|é|è|ê|ë)"
    I_VOWEL_FORMS = "(Í|Ì|Î|Ï|í|ì|î|ï)"
    O_VOWEL_FORMS = "(Ó|Ò|Ô|Ö|ó|ò|ô|ö)"
    U_VOWEL_FORMS = "(Ú|Ù|Û|Ü|ú|ù|û|ü)"
    N_FORMS = "ñ"
    C_FORMS = "(ç|þ)"  # For "Curaçao" and "Curaþao"
    PUNCTUATION_SYMBOLS = "(\.|,|-|:|;|_|`|'|´|!|¡|¿|\?|\^|¨)"


    @staticmethod
    def equals_ignore_case(str1, str2):
        if str1.lower() == str2.lower():
            return True
        return False

    #DONE
    @staticmethod
    def normalize_country_by_en_name(en_name):
        return CountryNormalizer._normalize_country_by_given_language_removable_expressions(en_name,
                                                                        CountryNormalizer.EN_REMOVABLE_EXPRESSIONS)
    @staticmethod
    def normalize_country_by_es_name(es_name):
        return CountryNormalizer._normalize_country_by_given_language_removable_expressions(es_name,
                                                                        CountryNormalizer.ES_REMOVABLE_EXPRESSIONS)
    @staticmethod
    def normalize_country_by_fr_name(fr_name):
        return CountryNormalizer._normalize_country_by_given_language_removable_expressions(fr_name,
                                                                        CountryNormalizer.FR_REMOVABLE_EXPRESSIONS)

    @staticmethod
    def _normalize_country_by_given_language_removable_expressions(original_string, given_exp):
        print "---------# NORMALIZER"
        result = str(original_string)
        print result
        result = CountryNormalizer._substitute_conflictive_chars(result)
        print result
        result = CountryNormalizer._delete_text_between_brackets(result)
        print result
        result = result.lower()
        print result
        result = CountryNormalizer._rem_words_by_language(result, given_exp)
        print result
        result = CountryNormalizer._rem_white_spaces(result)
        print result
        print "---------# NORMALIZER"

        return result

    @staticmethod
    def _rem_white_spaces(original_string):
        return original_string.replace(" ", "")


    @staticmethod
    def _delete_text_between_brackets(original_string):
        if original_string.__contains__("(") and original_string.__contains__(")"):
            index_beg = original_string.index("(")
            index_end = original_string.index(")") + 1
            return original_string[0:index_beg] + original_string[index_end:1]
        else:
            return original_string


    @staticmethod
    def _substitute_conflictive_chars(original_string):
        # print "MIRAD MI PENEEEEE"
        result = original_string
        result = re.sub(CountryNormalizer.A_VOWEL_FORMS, 'a', result)
        result = re.sub(CountryNormalizer.E_VOWEL_FORMS, 'e', result)
        result = re.sub(CountryNormalizer.I_VOWEL_FORMS, 'i', result)
        result = re.sub(CountryNormalizer.O_VOWEL_FORMS, 'o', result)
        result = re.sub(CountryNormalizer.U_VOWEL_FORMS, 'u', result)
        result = re.sub(CountryNormalizer.N_FORMS, 'n', result)
        result = re.sub(CountryNormalizer.C_FORMS, 'c', result)
        result = re.sub(CountryNormalizer.PUNCTUATION_SYMBOLS, " ", result)
        return result

    @staticmethod
    def _rem_words_by_language(original, sub_exp):
        #         regex_exp contains a list of non-significant words that should be replaced
        #         by a blank. To fit in the regex, each word should be in the middle of
        #         some of this pairs:
        #          - [white_space] word [white_space]
        #          - [white_space] word [end_of_string]
        #          - [start_of_the_string] word [end_of_string]
        #
        regex_exp = "(\A" + sub_exp + "\s)|(\s" + sub_exp + "\s)|(\s" + sub_exp + "\Z)"

        version1 = ""
        version2 = original
        while version1 != version2:
            version1 = version2
            version2 = re.sub(regex_exp, " ", version1)
            #         The previous loop, applying re.sub more than one time to the original chain
            #         should be done because if more than 1 unsignificant words come in a streak,
            #         some of them coul be ignored by the regex. E.g.: "Republic of the Congo".
            #         " of " will fit in the regex, but that means that " the " won´t be recognized.
            #         The white space between "of" and "the" will be used only in one of the substrings,
            #         so in fact we hace " of " and "the ", and the resultant string will be
            #         "Republic the Congo". If we apply more than one time the regex, this things
            #         would be avoided

        return version2

