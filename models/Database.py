import pyrebase
from requests.exceptions import HTTPError 
import json 

class Database(object):
    def __init__(self, token=None):
        self.firebase_conn = Database.__connect__()
        self.database = self.firebase_conn.database()
        self.auth = self.firebase_conn.auth()
        self.token = token
    
    def query(self, location, key=None, token=None):
        print "Location: "+ str(location)
        location = self.path_parse(location)
        if len(location) == 1: 
            ultimate_node = self.database.child(location[0])
            location = None
        else:
            ultimate_node = self.database.child(location[1])
            location = location[2:]
        if location is not None:
            for node in location:
                ultimate_node = ultimate_node.child(node)
            try:
                if token == None and self.token is not None:
                    token = self.token
                if key == None:
                    return ultimate_node.get(token).val()
                else:
                    return ultimate_node.child(key).get(token).val()
            except HTTPError as e: 
                print "Firebase GET: " + e.strerror
                return json.loads(e.strerror)
        
    def put(self, location, name, data, token=None):
        location = self.path_parse(location)
        ultimate_node = self.database.child(location[0])
        for node in location[1:]: 
            ultimate_node = ultimate_node.child(node)
        try: 
            if token is None and self.token is not None :
                token = self.token
            print ultimate_node.child(name).update(data, token)
        except HTTPError as e:
            print "Firebase POST: " + e.strerror + '\nLocation:'+ str(location) + '\nData: ' + str(data)
            return False
        return True
        
    def insert(self, location, data, token=None):
        location = self.path_parse(location)
        ultimate_node = self.database.child(location[0])
        result = None 
        for node in location[1:]:
            ultimate_node = ultimate_node.child(node)
        try:
            if token is None and self.token is not None:
                token = self.token
            print "Firebase SET:" + str(ultimate_node.set(data, token)) 
            print "Location" + str(location)
        except HTTPError as e: 
            print "Firebase SET: " + e.strerror  + '\nLocation:' + str(location) + '\nData: ' + str(data)
            return False
        return True
        
    def delete(self, location, key, token=None):
        location = self.path_parse(location)
        ultimate_node = self.database.child(location[0])
        for node in location[1:]:
            ultimate_node = ultimate_node.child(node)
        try:
            if token is None and self.token is not None:
                token = self.token
            ultimate_node.child(key).remove(token)
        except HTTPError as e: 
            return False
        return True
        
    def path_parse(self, location):
        if isinstance(location, (str, unicode)) and len(location) > 0:
            return location.split('/')
        else:
            return ['']
            
    def set_token(self, token):
        self.token = token 
    
    @staticmethod
    def __connect__():
        """ 
            Connect to the Firebase database 
        """
        import pyrebase
        
        config = {"apiKey": "AIzaSyBLOhr2voKEhut0Vch6tDQGiSLiwiy26vo", 
        "authDomain": "checkinapp-148816.firebaseapp.com", 
        "databaseURL": "https://checkinapp-148816.firebaseio.com", 
        "storageBucket": "checkinapp-148816.appspot.com"}
        
        return pyrebase.initialize_app(config)