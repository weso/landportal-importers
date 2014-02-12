'''
Created on 10/02/2014

@author: Dani
'''


if __name__ == '__main__':
    
    import re
#     from es.weso.countryrec.country_reconciler import CountryReconciler
#     from es.weso.countryrec.normalizer.country_name_normalizer import CountryNameNormalizer
    
#     rec = CountryReconciler()
#      
# #     config = ConfigParser()
# #     config.read("../../../../files/configuration.ini")
#     print len(rec.clist)
    
    sub_exp = "el|la|los|las|de|y|&"
    chain = "el cacas de la el los el los y huevos y su lamina electrica del copon las"
    
    sub_exp = "(el|las|los|la|lo|de|y|&|del)"
    s= chain
    for i in range(1,2):
        s = re.sub("(\A"+sub_exp+"\s)|(\s"+sub_exp+"\s)|(\s"+sub_exp+"\Z)" , " ", s)
    print chain
    print s
    print s.strip() 

    