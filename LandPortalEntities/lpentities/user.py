'''
Created on 02/02/2014

@author: Miguel Otero
'''

class User(object):
    '''
    classdocs
    '''


    def __init__(self, user_login, organization=None):
        '''
        Constructor
        '''
        self.organization = organization
        self.user_id = self._generate_id(user_login)

    @staticmethod
    def _generate_id(user_login):
        return "USR" + user_login.upper()




        # TODO : what about ip and timestamp? I think it would be better to catch this values when receiving data,
        # TODO : if the Receiver is a web service.