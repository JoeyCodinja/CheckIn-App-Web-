import random 
from datetime import datetime, timedelta
from PCLocations import PCLocations

import re

class Log:
    ARRIVE = 'arrive'
    LUNCH = 'lunch'     
    LEAVE = 'leave'
    CONFIRM = 'confirm'
    
    TYPES = [ARRIVE, LUNCH, LEAVE, CONFIRM]
    
    VALID_LOCATIONS = PCLocations.valid_locations
    
    def __init__(self, lid, ltype, who, 
                 when=None, loc=PCLocations.Unregistered, 
                 confirm_data=None, 
                 lunch_data=None, leave=None):
        if when is not None:
            self.__log_time = when
        else: 
            self.__log_time = datetime.now()
        
        if lunch_data is not None: 
            self.__lunch_time = lunch_data
        else:
            self.__lunch_time = {'start': 'null', 'end':'null'} 
        self.__lid = lid
        
        if loc not in Log.VALID_LOCATIONS and \
            str(loc) != PCLocations.Unregistered:
            raise ValueError('Invalid log location')     
        self.__location = loc
        self.__logger = who
        if leave is not None: 
            self.__leave == leave
        else:
            self.__leave = 'null'
        
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
    def logger(self):
        return self.__logger
        
    @property
    def is_confirmed(self):
        return self.__confirm_data['state']
    
    @property
    def log_id(self):
        return self.__lid
    
    @property
    def log_type(self): 
        return self.__ltype
    
    @property
    def log_location(self):
        return self.__location 
        
    @property
    def lunch_data(self):
        return self.__lunch_time
    
    def confirm_log(self, database, staff_id, confirm_time):
        staff = self.staff_members(database)
        if staff_id in staff:
            self.__confirm_data['state'] = True
            self.__confirm_data['time'] = confirm_time
            self.__confirm_data['who'] = staff_id
        return self
    
    def start_lunch(self):
        self.__lunch_time['start'] = datetime.now()
    
    def end_lunch(self):
        end_time = datetime.now()
        lunch_delta = end_time - self.__lunch_time['start']
        lunch_delta = 60 - (lunch_delta.seconds / 60)
        self.__lunch_time['end'] = lunch_delta
        print self.__lunch_time
            
    def depart(self):
        self.__leave = datetime.now().time().isoformat()[:8]
        
    @staticmethod
    def get_absent_interns(database, intern_list, timetable, u_id):
        logs = Log.from_db(database, u_id)
        today = datetime.now().date()
        from pprint import pprint
        for log in logs:
            intern_in_list = log.logger in intern_list
            todays_log = today == log._Log__log_time.date()
            try: 
                timetabled_today = [log.logger in timetable[today.strftime('%A')][times] for times in timetable[today.strftime('%A')]]
                timetabled_today = reduce(lambda x, y: x | y, timetabled_today)
                if intern_in_list:
                    if todays_log or not timetabled_today:
                        intern_list.remove(log.logger)
                else: 
                    continue
            except KeyError:
                # The day isn't a timetable-able day (Saturday, Sunday)
                return []
        return intern_list
                
    @staticmethod
    def from_db(database, u_id, key=None , date_start=None, date_end=None):
        def key_is_id(key):
            if re.match(r'\d{5}p', key):
                return True
            return False
        
        def transform_datetime(date, time=[]):
            if isinstance(time, (str, unicode)):
                if re.match(r'(\d{2}:){2}\d{2}', time):
                    time = time.split(':')
                    time = [[['hour','minute','second'][i], int(time[i])] for i in range(len(time))]
                else: 
                    return ValueError('Incorrect time format passed')
            if re.match(r'\d{4}-\d{2}-\d{2}', date):
                date = date.split('-')
                date = [[['year', 'month', 'day'][i], int(date[i])] for i in range(len(date))]
                date.extend(time)
                print date
                return datetime(**dict(date))
            else: 
                return ValueError('Incorrect date format passed')
        
        def construct_instance(key, data):
            instance_args = {'lid'  : key,
                             'ltype': data['type'],
                             'who'  : data['from'],
                             'when' : transform_datetime(data['date'],
                                                         data['arrive-time'])}
            date = data['date'] 
            try:
                have_confirmant = data['confirmed']['who'] is not None 
                time_confirmed = data['confirmed']['time'] is not None 
            except KeyError: 
                have_confirmant = False
                time_confirmed = False
                
            if have_confirmant and time_confirmed: 
                instance_args.update({'confirm_data': data['confirmed']})
                
            has_lunch_start = str(data['lunch-time']['start']) != 'null'
            has_lunch_end = str(data['lunch-time']['end']) != 'null'
            if has_lunch_start or (has_lunch_start and has_lunch_end): 
                # Has lunch data
                try:
                    data['lunch-time']['start'] = transform_datetime(data['date'], 
                                                                     data['lunch-time']['start'])
                    data['lunch-time']['end'] = data['lunch-time']['end']
                    instance_args.update({'lunch_data': data['lunch-time']})
                except (ValueError, AttributeError):
                    pass
            
            return Log(**instance_args)
        
        if u_id not in Log.staff_members(database) and u_id != key:
            # Should either be a staff member, 
            # or the persons own logs
            # TODO: Create AuthenticationRequiredException
            return ValueError('You do not have the authority to execute this action')
        
        if key is not None:
            if key_is_id(key):
                result = database.query('/log')
                if date_start or date_end:
                    log_list = []
                    for item in result: 
                        date_args = tuple(result[item]['date'].split('-'))
                        log_date = datetime.date(*date_args)
                        id_is_key = result[item]['from'] == key
                        if date_end:
                            if date_end >= log_date >= date_start and id_is_key:
                                log_list.append(construct_instance(item, result[item]))
                        else:
                            if log_date >= date_start and id_is_key: 
                               log_list.append(construct_instance(item, result[item]))
                    import pdb;pdb.set_trace()
                    return log_list
                    
                for item in result:
                    todays_log = result[item]['date'] == \
                        datetime.now().date().isoformat()
                    is_user_log = result[item]['from'] == key 
                    if todays_log and is_user_log:
                        return construct_instance(item, result[item])
                raise ValueError('Can\'t find a log for this user %s' % key)
            result = database.query('/log/%s' % key)
            try:
                return construct_instance(key, result[key])
            except TypeError:
                # result == None 
                raise ValueError('key passed does not reference any logs')
        else:
            result = database.query('/log')
            log_list = []
            try:
                for log in result:
                    log_list.append(construct_instance(log, result[log]))
                return log_list
            except TypeError:
                # No Logs in system
                return log_list 

    def to_db(self, database):
        from copy import copy 
        lunch_time = copy(self.__lunch_time)
        leave = copy(self.__leave)
        if lunch_time['start'] != 'null':
            lunch_time.update({'start':lunch_time['start'].time().isoformat()[:8]})
        data = {
                'from': self.__logger, 
                'type': self.__ltype,
                'date': datetime.now().date().isoformat(),
                'where': self.__location,
                'leave_time': self.__leave, 
                'arrive-time': self.__log_time.time().isoformat()[:8] if isinstance(self.__log_time, datetime) else self.__log_time,
                'lunch-time': lunch_time,
                'confirmed': self.__confirm_data
               }
        from pprint import pprint
        pprint(data)
        database.put('/log', self.__lid, data)
    
    @staticmethod 
    def staff_members(database):
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
    def to_file(self, database):
        pass 
    
    