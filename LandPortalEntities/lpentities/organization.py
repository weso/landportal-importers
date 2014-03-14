'''
Created on 02/02/2014

@author: Miguel Otero
'''

class Organization(object):
    '''
    classdocs
    '''


    def __init__(self, chain_for_id, name=None, url=None, description=None, url_logo=None, is_part_of=None):
        """
        Constructor

        """

        self.name = name
        self.url = url
        self.is_part_of = is_part_of
        self.description = description
        self.url_logo = url_logo

        self.data_sources = []
        self.users = []


        self.organization_id = self._generate_id(chain_for_id)


    @staticmethod
    def _generate_id(chain_for_id):
        return "ORG" + chain_for_id.upper()

    def add_user(self, user):
        self.users.append(user)
        user.organization = self

    def add_data_source(self, data_source):
        self.data_sources.append(data_source)
        data_source.organization = self