'''
Created on 10/02/2014

@author: Dani
'''


if __name__ == '__main__':
    
    from es.weso.countryrec.country_reconciler import CountryReconciler
    
    rec = CountryReconciler()
     
#     config = ConfigParser()
#     config.read("../../../../files/configuration.ini")
    print len(rec.clist)
    