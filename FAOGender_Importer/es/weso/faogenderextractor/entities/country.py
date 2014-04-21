'''
Created on 21/01/2014

@author: Miguel Otero
'''

class Country(object):
    '''
    classdocs
    '''


    def __init__(self, holdersTotal, womenHolders, coownershipHoldings, communalProperty,
                 womenHouseholds):
        '''
        Constructor
        '''
        self.holdersTotal = holdersTotal
        self.womenHolders = womenHolders
        self.coownershipHoldings = coownershipHoldings
        self.communalProperty = communalProperty
        self.womenHouseholds = womenHouseholds