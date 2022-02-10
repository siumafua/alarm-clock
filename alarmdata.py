import logging
import logconf

logger = logging.getLogger(__name__)

# -------- end logging config --------------

import sqlite3

class AlarmData():
    def __init__(self, dbname = "alarm.db"):
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()

    def alarmTableExists(self):
        try:
            self.cursor.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Alarms' ''')
            if self.cursor.fetchone()[0] == 1: 
                logger.info('alarmTableExists: Alarm table exists')
                return True                
            else:
                return False
        except Exception as e:
            logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))
            return False

    def createAlarmsTable(self) -> int:
        print("createalarm")
        try:
            #get the count of tables with the name
            sql = """ 
                CREATE TABLE Alarms 
                (creationdate text, name text primary key, hour int, min int, dura int, snooze int, days text, enable bool);
            """
            self.cursor.execute(sql)
            logger.info("createAlarmTable: Executing {}".format(sql))
            logger.info('createAlarmTable: Successfully created Alarm table')
            return 1 
        except sqlite3.OperationalError as o:
            logger.error("Error Type : {}, Error Message : {}".format(type(o).__name__, o))
            return -1

        except Exception as e:
            logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))
            return 0 

    def dropTable(self):
        try:
            self.cursor.execute("DROP TABLE Alarms;")
            self.conn.commit()
            logger.info("dropTable: Successfully delete Alarms table")
            print("drop table")
            return True

        except sqlite3.OperationalError as o:
            logger.error("Error Type : {}, Error Message : {}".format(type(o).__name__, o))

        except Exception as e:
            logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))

        return False

    def insertTestData(self):
        try:
            self.cursor.executemany("INSERT INTO Alarms VALUES (?, ?, ?, ?, ?, ?, ?, ?);", [
                ('07-02-2021', 'alarm1', 6,  0, 1, 0, 'Mon, Tue',            True),
                ('07-02-2021', 'alarm2', 6,  0, 2, 0, 'Sat, Sun',            True),
                ('07-02-2021', 'alarm3', 14, 0, 3, 0, 'Mon, Tue',            True),
                ('07-02-2021', 'alarm4', 16, 0, 4, 0, 'Tue, Wed, Thur, Fri', True)
            ])
            self.conn.commit()
            return True

        except sqlite3.OperationalError as o:
            logger.error("Error Type : {}, Error Message : {}".format(type(o).__name__, o))

        except Exception as e:
            logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))

        return False

    def insertRecord(self, rec = ()):
        try:
            self.cursor.execute("INSERT INTO Alarms VALUES (?, ?, ?, ?, ?, ?, ?, ?);", rec) 
            self.conn.commit()
            logger.info("insertRecord: successfully adding {}".format(rec))
            return True

        except sqlite3.OperationalError as o:
            logger.error("Error Type : {}, Error Message : {}".format(type(o).__name__, o))

        except Exception as e:
            logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))
            return False

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

    def closeConn(self):
        try:
            self.conn.close()
            logger.info("closeConn: Successfully closing DB connection")
            return True

        except Exception as e:
            logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))
            return False


###
# Class Quick Test 
###
"""
data = AlarmData()
if data.createAlarmsTable() == -1:
    print("droptable")
    data.dropTable()
    data.createAlarmsTable()
    logger.info("Dropping and recreating Alarm table")
else:
    logger.error(":Creating Alarm table failed. ")
    exit()

data.insertTestData()

print("getAll")
print(data.getAll())

data.insertRecord(('07-02-2021', 'alarm5', 6, 0, 10, 1, 'Mon, Tue', True))
data.insertRecord(('07-02-2021', 'alarm6', 6, 0, 11, 2, 'Mon, Tue', False))
print("get one or more")
print(data.getAlarmByName('alarm4'))
print("Active")
print(data.getActiveAlarm())
print("Inactive")
print(data.getInactiveAlarm())
"""