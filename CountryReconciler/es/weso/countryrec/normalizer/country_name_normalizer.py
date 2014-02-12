'''
Created on 10/02/2014

@author: Dani
'''
import re
class CountryNameNormalizer(object):
    
    SUB_EXP_ES = "(el|las|los|la|lo|de|y|&|del|en)"
    SUB_EXP_EN = "(the|in|of|and|&)"
    SUB_EXP_FR = "(les|las|le|la|et|&|dans|de|d)"

    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    @staticmethod
    def normalize_es_country(original):
        result = CountryNameNormalizer.general_normalization(original)
        result = CountryNameNormalizer.rem_words_by_languaje(result, CountryNameNormalizer.SUB_EXP_ES)
        return result
    
    @staticmethod
    def normalize_fr_country(original):
        result = CountryNameNormalizer.general_normalization(original)
        result = CountryNameNormalizer.rem_words_by_languaje(result, CountryNameNormalizer.SUB_EXP_FR)
        return result
    
    @staticmethod
    def normalize_en_country(original):
        result = CountryNameNormalizer.general_normalization(original)
        result = CountryNameNormalizer.rem_words_by_languaje(result, CountryNameNormalizer.SUB_EXP_EN)
        return result
    
    @staticmethod
    def rem_words_by_languaje(original, sub_exp):
#         
#         regex_exp contains a list of non-significant words that should be replaced
#         by a blank. To fit in the regex, each word should be in the middle of
#         some of this pairs:
#          - [white_space] word [white_space]
#          - [white_space] word [end_of_string]
#          - [start_of_the_string] word [end_of_string]
#         
        regex_exp = "(\A"+sub_exp+"\s)|(\s"+sub_exp+"\s)|(\s"+sub_exp+"\Z)"
        
        version1 = original
        version2 = ""
        while version1 != version2:
            version1 = version2
            version2 = re.sub( regex_exp, " ", version1)
#         The previous loop, applying re.sub more than one time to the original chain
#         should be done because if more than 1 unsignificant words come in a streak,
#         some of them coul be ignored by the regex. E.g.: "Republic of the Congo". 
#         " of " will fit in the regex, but that means that " the " won´t be recognized.
#         The white space between "of" and "the" will be used only in one of the substrings,
#         so in fact we hace " of " and "the ", and the resultant string will be 
#         "Republic the Congo". If we apply more than one time the regex, this things 
#         would be avoided
        
        return version2
    
    @staticmethod
    def general_normalization(original):
        result = original.lower()
        result = CountryNameNormalizer.substitute_conflictive_chars(result)
        result = result.strip()
        
        return result
        
    @staticmethod
    def substitute_conflictive_chars(original):
        result = original
        #Vowel a
        result = re.sub("à|á|â|ä", "a", result)
        #Vowel e
        result = re.sub("é|è|ê|ë", "e", result)       
        #Vowel i
        result = re.sub("í|ì|î|ï", "i", result)
        #Vowel o
        result = re.sub("ó|ò|ö|ô", "o", result)
        #Vowel u
        result = re.sub("ù|ú|û|ü", "u", result)
        #Char ç
        result = re.sub("ç", "c", result)
        #char ñ
        result = re.sub("ñ", "n", result)
        #special chars
        result = re.sub("¨|'|`|´|^|!|¡|?|¿", " ", result)
        #----------return
        return result
        
        