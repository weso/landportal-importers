__author__ = 'Dani'


class Deal(object):

    #Negotiation status
    INTENDED = "Intended"
    CONCLUDED = "Concluded"
    FAILED = "Failed"

    #Sectors
    AGRICULTURE = "Agriculture"
    CONSERVATION = "Conservation"
    FORESTRY = "Forestry"
    INDUSTRY = "Industry"
    RENEWABLE_ENERGY = "RenewableEnergy"
    TOURISM = "Tourism"
    OTHER = "Other"
    UNKNOWN = "Unknown"



    def __init__(self, target_country=None, production_hectares=None, contract_hectares=None,
                 intended_hectares=None, date=None, sectors=None, negotiation_status=None):
        self.target_country = target_country
        self.production_hectares = production_hectares
        self.contract_hectares = contract_hectares
        self.intended_hectares = intended_hectares
        self.date = date
        self.sectors = sectors
        self.negotiation_status = negotiation_status


