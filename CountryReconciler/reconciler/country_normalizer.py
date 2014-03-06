# -*- coding: utf-8 -*-

"""
Created on 10/02/2014

@author: Dani
"""

import re
from string import capitalize

from reconciler.entities.normalized_country import NormalizedCountry
from reconciler.exceptions.unknown_country_error import UnknownCountryError


class CountryNormalizer(object):
    """
    In this class we'll implement the normalizer methods responsible
    for returning a NormalizedCountry object from a certain distinctive
    value. If a reconciliation is needed we'll also implement it here.
    """

    # Conflictive expressions
    EN_REMOVABLE_EXPRESSIONS = "(The|the|in|of|and|&)"
    REMOVABLE_CHARACTERS = "(¨|'|`|´|^|,|.|;|!|¡|?|¿| )"
    A_VOWEL_FORMS = "(Á|À|Â|Ä|á|à|â|ä)"
    E_VOWEL_FORMS = "(É|È|Ê|Ë|é|è|ê|ë)"
    I_VOWEL_FORMS = "(Í|Ì|Î|Ï|í|ì|î|ï)"
    O_VOWEL_FORMS = "(Ó|Ò|Ô|Ö|ó|ò|ô|ö)"
    U_VOWEL_FORMS = "(Ú|Ù|Û|Ü|ú|ù|û|ü)"
    N_FORMS = "ñ"
    C_FORMS = "(ç|þ)"  # For "Curaçao" and "Curaþao"

    def __init__(self):
        pass # Por el momento...


    @staticmethod
    def equals_ignore_case(str1, str2):
        if str1.lower() == str2.lower():
            return True
        return False

    #TODO : Revisar si hace lo que debe
    def normalize_country_by_en_name(self, en_name):
        for country in self.parsed_countries:
            if country.sname_en is not None:
                if self.equals_ignore_case(en_name, country.sname_en):
                    return NormalizedCountry(country.sname_en, country.get_iso3())
                else:
                    ret = self.reconcile_country_by_en_name(en_name, country)
                    if ret is not None:
                        return ret
        raise UnknownCountryError('Unknown country for EN name ' + en_name)

    #TODO: Revisar primer if. Seguramente sacar a otro metodo, pero aparte prepararlo para
    #TODO: zumbarse todo lo que venga entre paréntesis
    def substitute_conflictive_chars(self, string):
        if str(string).__contains__('('):
            end = string.index('(')
            string = string[:end - 1]  # For the blank space between the end of the name and the '('
        string = re.sub(self.A_VOWEL_FORMS, 'a', string)
        string = re.sub(self.E_VOWEL_FORMS, 'e', string)
        string = re.sub(self.I_VOWEL_FORMS, 'i', string)
        string = re.sub(self.O_VOWEL_FORMS, 'o', string)
        string = re.sub(self.U_VOWEL_FORMS, 'u', string)
        string = re.sub(self.N_FORMS, 'n', string)
        string = re.sub(self.C_FORMS, 'c', string)
        return string

    #TODO: Revisar si hace lo que debe
    def normalize_country_by_es_name(self, es_name):
        for country in self.parsed_countries:
            if country.sname_es == es_name:
                return NormalizedCountry(country.sname_en, country.get_iso3())
        raise UnknownCountryError('Unknown country for ES name ' + es_name)

    #TODO: Revisar si hace lo que debe
    def normalize_country_by_fr_name(self, fr_name):
        for country in self.parsed_countries:
            if country.sname_fr == fr_name:
                return NormalizedCountry(country.sname_en, country.get_iso3())
        raise UnknownCountryError('Unknown country for FR name ' + fr_name)