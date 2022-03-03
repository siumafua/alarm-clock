from alarmdata import AlarmData
from datetime import datetime

if __name__ == '__main__':

    data = AlarmData()
    if data.is_exists:
        print("recreating table")
        data.drop_table()
        data.create_alarms_table()

    data.insert_record(('07-02-2021', 'alarm1', 'work: morning', '18:00', 5, 5, 'Sun', 'resources/default.mp3', True))
    data.insert_record(('07-02-2021', 'alarm2', 'work: lunch','09:00', 5, 5, 'Sat, Sun', 'resources/default.mp3', True))
    data.insert_record(('07-02-2021', 'alarm3', 'work: finish','08:00', 5, 5, 'Mon, Tue, Wed, Thur, Fri', 'resources/default.mp3', True))
    data.insert_record(('07-02-2021', 'alarm4', 'church morning','10:00', 5, 5, 'Sat, Sun, Mon', 'resources/default.mp3', False))
    data.insert_record(('07-02-2021', 'alarm5', 'church evening','14:00', 5, 5, 'Mon, Tue', 'resources/default.mp3', False))

    rec = {
        'date': datetime.now().strftime("%d-%m-%Y"), 
        'name': 'alarm1',
        'alarmtime': '08:10',
        'dura': 5,
        'snooze': 5,
        'days': 'Mon,Tue',
        'audio': 'resources/default.mp3',
        'enable': 1
    }

    data.update_record('name', rec)
    print("getAll")
    print(data.alarms)

    print("get one or more")
    res = data.get_alarm_by_field('name', 'alarm1')
    print(res)


    print("Updating alarmtime")
    rec = ('alarm1','alarmtime','20:00')
    data.update_record(rec)
    res = data.get_alarm_by_field('name', 'alarm1')

    print("updating alarmtime all fields")
    rec = ('alarmtime','21:05')
    data.update_record(rec)
    print(data.alarms)


    print("Active")
    print(data.active_alarms)
    print("Inactive")
    print(data.inactive_alarms)

