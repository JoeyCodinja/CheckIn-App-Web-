import calendar
from datetime import datetime, timedelta
from collections import OrderedDict


class Timetable:
    DAYS = OrderedDict([[day, calendar.day_name[day]]for day in range(len(calendar.day_name[:5]))])
    
    def __init__(self, timetable=None):
        if timetable is not None:
            self.timetable = timetable
        else:
            self.timetable = self._generate(timetable)
    
    def _generate(self, data):
        timetable = OrderedDict([[day, OrderedDict()] for day in calendar.day_name[:5]])
        start_time = datetime.now().replace(
            hour=8, 
            minute=0, 
            second=0, 
            microsecond=0)
        end_time = datetime.now().replace(
            hour=20, 
            minute=0, 
            second=0, 
            microsecond=0)
        time_slot = timedelta(hours=1)
        for day in timetable: 
            day_finished = False
            time = start_time
            while(not day_finished):
                if time > end_time:
                    day_finished = True
                else:
                    timetable[day].update({time.time().isoformat()[:5]: ['null']})
                    time += time_slot
            
        return timetable
        
    def assign(self, day, time_info, uid):
        time_isdict   = isinstance(time_info, dict)
        has_starttime = 'start' in time_info
        has_endtime   = 'end' in time_info
        if not(time_isdict and has_starttime and has_endtime):
            raise ValueError('Argument \'time\' is malformed')
        try: 
            times = self.timetable[day].keys()
            range_start = False
            for time in times: 
                if time == time_info['start']:
                    if 'null' in self.timetable[day][time] :
                        self.timetable[day][time].remove('null')
                    if uid not in self.timetable[day][time]:
                        self.timetable[day][time].append(uid)
                    range_start = True
                elif range_start:
                    if 'null' in self.timetable[day][time]:
                        self.timetable[day][time].remove('null')
                    if uid not in self.timetable[day][time]:
                        self.timetable[day][time].append(uid)
                    
                if time == time_info['end']:
                    range_start = False
            return self
        except KeyError:
            raise ValueError('Argument \'day\' is invalid')
            
    def unassign(self, day, time, uid):
        correct_format = isinstance(time, dict) and 'start' in time and 'end' in time
        range_start = False
        if not correct_format:
            raise ValueError('time argument passed is malformed')
        
        for times in self.timetable[day]:
            if times == time['start']: 
                range_start= True
            if range_start: 
                if uid in self.timetable[day][times] and len(self.timetable[day][times]) == 1:
                    self.timetable[day][times].append('null')
                self.timetable[day][times].remove(uid)
            if times == time['end']:
                return self
        
    def list_interns(self, day, time=None):
        def remove_duplicates(array):
            for item in array:
                try: 
                    if array.index(array[:array.index(item)]) > -1: 
                        array.remove(item)
                except ValueError as e: 
                    if array.index(item) == len(array)-1:
                        array.pop()
            
            return array
            
        if time is not None: 
            pass 
        interns = [] 
        for time in self.timetable[day]:
            if self.timetable[day][time] == []:
                continue
            if self.timetable[day][time] not in interns:
                interns.extend(self.timetable[day][time])
        return interns    
        
        
    @staticmethod
    def from_db(database): 
        def order_timetable_data(data):
            days = data.keys()
            days = sorted(days, key=lambda day: list(calendar.day_name).index(day))
            sorted_data = OrderedDict()
            for day in days: 
                times = data[day].keys()
                times = sorted(times, key=lambda time: int(time[:2]))
                sorted_times = OrderedDict()
                for time in times:
                    sorted_times.update({time: data[day][time]})
                sorted_data.update({day: sorted_times})
            return sorted_data
                    
        result = database.query('/timetable')
        if result == None:
            return Timetable()
        else: 
            result = order_timetable_data(result)
            return Timetable(result)
    
    def to_db(self, database):
        database.put('/', 'timetable', self.timetable)
        