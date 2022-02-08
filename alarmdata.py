import logging
from os import path
from logging import config

log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
print(log_file_path)
config.fileConfig(log_file_path)
logger = logging.getLogger(__name__)


import sqlite3

class AlarmData():
    def __init__(self, dbname = "alarm.db"):
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()

    def alarmTableExists(self):
        try:
            self.cursor.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Alarms' ''')
            if self.cursor.fetchone()[0] == 1: 
                return True                
            else:
                return False
        except:
            return False

    def createAlarmsTable(self):
        try:
            #get the count of tables with the name
            self.cursor.execute(""" 
                CREATE TABLE Alarms 
                (creationdate text, name text primary key, hour int, min int, dura int, snooze int, days text, enable bool);
            """)

        except: 
            print("Error while creating Alarms table")
            return False
        else:
            return True

    def dropTable(self):
        try:
            self.cursor.execute("DROP TABLE Alarms;")
            self.conn.commit()
        except:
            print("Error while dropping Alarms table")
            return False
        else:
            return True

    def insertTestData(self):
        try:
            self.cursor.executemany("INSERT INTO Alarms VALUES (?, ?, ?, ?, ?, ?);", [
                ('07-02-2021', 'alarm1', 6, 0, 'Mon, Tue', True),
                ('07-02-2021', 'alarm2', 6, 0, 'Sat, Sun', True),
                ('07-02-2021', 'alarm3', 14, 0, 'Mon, Tue', True),
                ('07-02-2021', 'alarm4', 16, 0, 'Tue, Wed, Thur, Fri', True)
            ])
            self.conn.commit()
        except:
            print("Error while inserting test data")
            return False
        else:
            return True

    def insertRecord(self, rec = ()):
        try:
            self.cursor.execute("INSERT INTO Alarms VALUES (?, ?, ?, ?, ?, ?);", rec) 
            self.conn.commit()
        except:
            print("Error while inserting new record")
            return False
        else:
            return True

    def getInactiveAlarm(self):
        q = "SELECT * FROM Alarms WHERE enable = False;"
        self.cursor.execute(q)
        return self.cursor.fetchall() 

    def getActiveAlarm(self):
        q = "SELECT * FROM Alarms WHERE enable = True;"
        self.cursor.execute(q)
        return self.cursor.fetchall() 

    def getAlarmByDate(self, date):
        q = "SELECT * FROM Alarms WHERE creationdate = '{}';"
        q = q.format(date)
        self.cursor.execute(q)
        return self.cursor.fetchall() 

    def getAlarmByName(self, key):
        q = "SELECT * FROM Alarms WHERE name = '{}';"
        q = q.format(key)
        self.cursor.execute(q)
        return self.cursor.fetchall() 

    def getAll(self):
        self.cursor.execute("SELECT * FROM Alarms;")
        return self.cursor.fetchall() 

    def close(self):
        try:
            self.conn.close()
        except:
            print("Error while closing database connection")
            return False
        else:
            return True

"""
###
Class Quick Test 
###

data = AlarmData()
if data.createAlarmsTable() == False:
    data.dropTable()
    data.createAlarmsTable()

data.insertTestData()

print("getAll")
print(data.getAll())

data.insertRecord(('07-02-2021', 'alarm5', 6, 0, 'Mon, Tue', True))
data.insertRecord(('07-02-2021', 'alarm6', 6, 0, 'Mon, Tue', False))
print("get one or more")
print(data.getAlarmByName('alarm4'))
print("Active")
print(data.getActiveAlarm())
print("Inactive")
print(data.getInactiveAlarm())
"""