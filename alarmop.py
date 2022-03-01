from time import strftime
from kivy.clock import Clock
from datetime import datetime
from alarmdata import AlarmData
import re
from kivy.properties import(
    ListProperty,
    NumericProperty
)

class AlarmOp:
    def __init__(self) -> None:
        self.alarms = list()
        self.__get_alarms()

    def refresh(self, nap): #nap uses if called from Clock.schedule functions
        self.__get_alarms()

    def monitor_alarm(self) -> dict:
        ct = datetime.now()
        for alarm in self.alarms:
            if ct.weekday() in alarm['days']:
                if ct.hour == alarm['hour'] and \
                   ct.minute == alarm['min'] and  \
                   ct.second < 10: # just to be safe
                    return alarm
        return dict() # empty dict

    def __get_alarms(self) -> None:
        db = AlarmData()
        alarms_data = db.get_active_alarms()
        db.close_conn()

        list_holder = list()
        days = list(enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']))
        numeric_days = list()


        for alarm in alarms_data:
            # list of select days with white spaces removed
            # list is used to create a numeric list correspond to the
            # selected days.. Mon = 0, Tue = 1, ...
            alarm_days = list(map(lambda x: re.sub("\s+", '', x), alarm['days'].split(',')))
            numeric_days.clear()
            for j in range(len(alarm_days)):
                for x, day in days:
                    if alarm_days[j] == day:
                        numeric_days.append(x)

            # add to the final list
            list_holder.append({'hour': int((alarm['alarmtime'])[:2]), 'min': int((alarm['alarmtime'])[3:]),
                               'dura': int(alarm['dura']), 'snooze': int(alarm['snooze']),
                               'audio': alarm['audio'], 'days': numeric_days[:]})

        # clearing and reloading of data
        self.alarms.clear()
        self.alarms = list_holder[:]
                

    
