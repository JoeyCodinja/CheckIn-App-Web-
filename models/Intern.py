from Personnel import Personnel
from punchin_utils import Utils

class Intern(Personnel):
    INTERN = 90
    
    def __init__(self, database, name, p_id, email, last_state=None):
        super(Intern, self).__init__(name, p_id, last_state)
        self.__email = email
        self.database = database or None
        
    def getEmail(self):
        return Utils.parse_email_id(self.__email)
        
    def register(self, data):
        intern_information = dict(id=None)
    
    @staticmethod
    def is_an(database, email):
        if database is None:
            raise TypeError('No database instance given')
    
        query = database.query('/user', email.split('@')[0])
        
        return query['userType'] == Intern.INTERN
        
    
    @staticmethod
    def from_db(database, key=None):
        # If key is passed return specific key 
        # If key is None, return all interns
        INTERN = 90 
        listing = []
        users_fromdb = database.query('/user')
        print "DB Query for Intern Listing:\n" + str(users_fromdb)
        for user in users_fromdb:
            user_details = users_fromdb[user]
            if user_details['userType'] == INTERN:
                user_details = users_fromdb[user]
                try:
                    listing.append(Intern(database,
                                          user_details['name'],
                                          user_details['id'],
                                          user+'@gmail.com',
                                          user_details['lastState']))
                except KeyError:
                    listing.append(Intern(database,
                                          user_details['name'],
                                          user_details['id'],
                                          user+'@gmail.com'))
                                          
        return listing
                    