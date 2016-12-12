from Personnel import Personnel
from punchin_utils import Utils

class Staff(Personnel):
    STAFF = 10 
    
    BEGIN = 0 
    PUNCHED_IN = 2 
    LUNCH_START = 4
    LUNCH_END = 5
    
    def __init__(self, database, name, p_id, email, last_state=None,):
        super(Staff, self).__init__(name, p_id, last_state)
        self.__email = email
        self.database = database or None 
        
    def getEmail(self):
        return Utils.parse_email_id(self.__email)

    def register(self, database, data):
        staff_information = dict(id=None,
                             FCM_ID=None,
                             APP_ID=None, 
                             name=None,
                             isValidated=False,
                             userType=Staff.STAFF,
                             lastState=Staff.BEGIN)
        
        database.insert('/users', data['email'], staff_information)
    
    @staticmethod
    def is_an(database, email):
        if database is None:
            raise TypeError('No database instance given')
            
        query = database.query('/user', email.split('@')[0])
        
        return query['userType'] == Staff.STAFF
    
    @staticmethod    
    def from_db(database, key=None):
        # If key is passed return specific key
        # If key is None, return all staff
        STAFF = 10 
        ADMINSTAFF = 8
        listing = []
        users_fromdb = database.query('/user')
        print "DBQuery for Staff Listing:\n" + str(users_fromdb)
        for user in database.query('/user'):
            user_details = users_fromdb[user]
            if user_details['userType'] in (STAFF, ADMINSTAFF):
                try:
                    listing.append(Staff(database,
                                         user_details['name'], 
                                         user_details['id'],
                                         user+'@gmail.com',
                                         user_details['lastState']))
                except KeyError:
                    listing.append(Staff(database,
                                         user_details['name'],
                                         user_details['id'],
                                         user+'@gmail.com'))
        return listing
        