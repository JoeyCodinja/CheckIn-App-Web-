import random 
from datetime import datetime
import re

class Log:
    ARRIVE = 'arrive'
    LUNCH = 'lunch'
    LEAVE = 'leave'
    CONFIRM = 'confirm'
    
    TYPES = [ARRIVE, LUNCH, LEAVE, CONFIRM]
    
    def __init__(self, lid, ltype, who, confirm_data=None):
        self.__log_time = datetime.now().time().isoformat()[:8]
        self.__lid = lid
        self.__logger = who
        
        if ltype not in Log.TYPES: 
            raise ValueError('Invalid log type')
        else: 
            self.__ltype = ltype
        
        if confirm_data is not None: 
            if self.__validate_confirm_data(confirm_data):
                self.__confirm_data = confirm_data
            else:
                raise ValueError('Malformed confirmation data passed')
        else: 
            self.__confirm_data = {'who':None, 
                                   'state':False, 
                                   'time':None}
                                   
    def __validate_confirm_data(self, data):
        has_time = 'time' in data
        has_confirmer = 'who' in data
        has_state = 'state' in data 
        if has_time and has_confirmer and has_state:
            return True
        else: 
            return False 
        
    @property
    def is_confirmed(self):
        return self.__confirm_data['state']
    
    @property
    def log_id(self):
        return self.__lid
    
    @property
    def log_type(self): 
        return self.__ltype
    
    def confirm_log(self, staff_id, confirm_time):
        staff = self.staff_members
        if staff_id in staff:
            self._confirmed = True
            self.time_confirmed = confirm_time
    
    def set_log_time(self, new_time, u_id):
        time_pattern = r'(\d{2}:){2}\d{2}'
        if u_id in self.staff_members: 
            if re.match(time_pattern, new_time):
                self.__log_time = new_time
            else:
                raise ValueError('Invalid time format passed')
        else:
            # TODO: Create AuthenticationRequiredException
            raise ValueError('You do not have the authority to execute this action')
            
    @staticmethod
    def from_db(database, key=None):
        def construct_instance(key, data):
            instance_args = {'lid'  : key,
                             'ltype': data['type'],
                             'who'  : data['from']}
            have_confirmant = data['confirmed']['who'] is not None 
            time_confirmed = data['confirmed']['time'] is not None 
            if have_confirmant and time_confirmed: 
                instance_args.update({'confirm_data': data['confirmed']})
            return Log(**instance_args)
            
        if key is not None:
            result = database.query('/log/%s' % key)
            try:
                return construct_instance(key, result[key])
            except TypeError:
                # result == None 
                raise ValueError('key passed does not reference any logs')
        else:
            result = database.query('/log')
            log_list = []
            for log in result:
                log_list.append(construct_instance(log, result[log]))
            return log_list

    def to_db(self, database):
        data = {
                'from': self.__logger, 
                'type': self.__ltype,
                'time': self.__log_time,
                'confirmed': self.__confirm_data
               }
                
        database.put('/log', self.__lid, data)
    
    @property
    def staff_members(self, database):
        STAFF = 10
        ADMIN = 40
        
        users = database.query('/user')
        staff_members = []
        for user in users:
            is_staff = users[user]['userType'] == STAFF
            is_staffadmin = users[user]['userType'] == STAFF & ADMIN
            is_admin = users[user]['userType'] == ADMIN
            if is_staff or is_staffadmin or is_admin:
                staff_members.append(users[user]['id'])
        return staff_members
        
        
    # TODO: write Logs to file
    def to_file(database):
        pass 
    
    