class Unregistered(object):
    def __init__(self, email_id, name):
        self.__name = name
        self.__email_id = email_id
    
    def getName(self):
        return self.__name
        
    def getEmail(self):
        return self.__email_id
    
    @staticmethod
    def from_db(database, key=None):
        listing = [] 
        users_fromdb = database.query('/unregistered')
        print "DB Query for Unregistered Listing:\n" + str(users_fromdb)
        if users_fromdb == None:
            return [] 
        for user in users_fromdb:
            user_details =  users_fromdb[user]
            listing.append(Unregistered(user+"@gmail.com", 
                                        user_details['name']))
        
        return listing
        