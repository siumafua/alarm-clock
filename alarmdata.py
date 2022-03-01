#import logging
#import logconf
#logger = logging.getlogger(__name__)

# -------- end logging config --------------
import sqlite3
from functools import singledispatchmethod
from kivy.logger import Logger

class AlarmData:
    """
    AlarmData Store alarms' details.
    """
    def __init__(self, dbname = "resources/alarm.db"):
        self.conn = sqlite3.connect(dbname)
        self.conn.row_factory = sqlite3.Row
#        self.conn.create_function("concat", 2, self.__concat)
        self.cursor = self.conn.cursor()


    def alarm_table_exists(self) -> bool:
        try:
            self.cursor.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Alarms' ''')
            if self.cursor.fetchone()[0] == 1: 
                return True
#                #logger.info('alarmTableExists: Alarm table exists')
            else:
                return False
        except Exception as e:
            return False
#            #logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))

    def create_alarms_table(self) -> int:
        try:
            sql = """ 
                CREATE TABLE Alarms 
                    (creationdate text, 
                     name text primary key, 
                     alarmtime text, 
                     dura int, 
                     snooze int, 
                     days text, 
                     audio text, 
                     enable bool);
            """
            self.cursor.execute(sql)
            return 1
#            #logger.info("createAlarmTable: Executing {}".format(sql))
#            #logger.info('createAlarmTable: Successfully created Alarm table')
        except sqlite3.OperationalError as o:
            return -1
#            #logger.error("Error Type : {}, Error Message : {}".format(type(o).__name__, o))
        except Exception as e:
            return 0
#            #logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))

    def del_records(self, field: str, values: list) -> bool:
        n = len(values)
        sql = "DELETE FROM Alarms WHERE {} = {} ".format(field, values[0])
        for x in range(1, n-1):
            sql = sql + "OR '{}' ".format(values[x])
        sql = sql + "OR '{}'".format(values[n-1])
        print(sql)
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except sqlite3.OperationalError as o:
            print('Op error')
            return False
#            #logger.error("Error Type : {}, Error Message : {}".format(type(o).__name__, o))
        except Exception as e:
            print('other error')
            return False
#            #logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))
        return False

    def drop_table(self) -> bool:
        try:
            self.cursor.execute("DROP TABLE Alarms;")
            self.conn.commit()
#            #logger.info("dropTable: Successfully delete Alarms table")
            print("drop table")
            return True
        except sqlite3.OperationalError as o:
            return False
#            #logger.error("Error Type : {}, Error Message : {}".format(type(o).__name__, o))
        except Exception as e:
            return False
#            #logger.error("Error Type                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      : {}, Error Message : {}".format(type(e).__name__, e))
        return False

    @singledispatchmethod
    def update_record(self) -> bool:
        raise NotImplementedError("Error: Overloaded method has not being impletmented.")

    @update_record.register
    def _(self, rec: tuple) -> bool:

        # minimum 3 params provided
        if(len(rec) == 3):
            if type(rec[2])==str:
                sql = "UPDATE Alarms SET {}='{}' WHERE name='{}'".\
                    format(rec[1], rec[2], rec[0])
            else:
                sql = "UPDATE Alarms SET {}={} WHERE name='{}'".\
                    format(rec[1], rec[2], rec[0])
        elif(len(rec) == 2):
            if type(rec[1])==str:
                sql = "UPDATE Alarms SET {}='{}'".\
                    format(rec[0], rec[1])
            else:
                sql = "UPDATE Alarms SET {}={}".\
                    format(rec[0], rec[1])
        else:
            return False

        try:
            self.cursor.execute(sql) 
            self.conn.commit()
            return True
#            #logger.info("insertRecord: successfully adding {}".format(rec))
        except sqlite3.OperationalError as o:
            print("Error Type : {}, Error Message : {}".format(type(o).__name__, o))
            return False
#           #logger.error("Error Type : {}, Error Message : {}".format(type(o).__name__, o))

        except Exception as e:
            print("Error Type : {}, Error Message : {}".format(type(e).__name__, e))
            return False
#            #logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))
        return False


    @update_record.register
    def _(self, key: str, rec: dict) -> bool:
        print("call with dict")

        if len(rec) < 1:
            return False

        sql ="UPDATE Alarms SET "
        for k,v in rec.items():
            if k == key or k == 'date': 
                continue
            if k in ['name','alarmtime','audio','days']:
                sql = "{}{} = \'{}\',".format(sql, k, v)
            else:
                sql = "{}{} = {},".format(sql, k, int(v))
        sql = "{} WHERE {} = '{}'".format(sql[:len(sql)-1], key, rec[key])
        print("update SQL: " + sql)
        try:
            self.cursor.execute(sql) 
            self.conn.commit()
            return True
#            #logger.info("insertRecord: successfully adding {}".format(rec))
        except sqlite3.OperationalError as o:
            print("Error Type : {}, Error Message : {}".format(type(o).__name__, o))
            return False
#           #logger.error("Error Type : {}, Error Message : {}".format(type(o).__name__, o))

        except Exception as e:
            print("Error Type : {}, Error Message : {}".format(type(e).__name__, e))
            return False
#            #logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))
        return False


    @singledispatchmethod
    def insert_record(self, rec) -> bool:
        raise NotImplementedError("Error: Overloaded method has not being impletmented.")

    @insert_record.register
    def _(self, rec: dict) -> bool:
        v = tuple(rec.values())
        s = "?, " * len(rec.keys())
        s = "({})".format(s[:len(s)-2])
        sql="INSERT INTO Alarms VALUES "
        sql = sql + "{}".format(s)        
        try:
            self.cursor.execute(sql, v) 
            self.conn.commit()
            return True
#            #logger.info("insertRecord: successfully adding {}".format(rec))
        except sqlite3.OperationalError as o:
            return False
#           #logger.error("Error Type : {}, Error Message : {}".format(type(o).__name__, o))

        except Exception as e:
            return False
#            #logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))
        return False

    @insert_record.register
    def _(self, rec: tuple) -> bool:
        try:
            sql = """
                   INSERT 
                   INTO Alarms 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                   """
            self.cursor.execute(sql, rec) 
            self.conn.commit()
            return True
#            #logger.info("insertRecord: successfully adding {}".format(rec))
        except sqlite3.OperationalError as o:
            return False
#           #logger.error("Error Type : {}, Error Message : {}".format(type(o).__name__, o))

        except Exception as e:
            return False
#            #logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))
        return False
        
    def get_inactive_alarms(self) -> list:
        sql = """SELECT 
                 name, alarmtime, dura, snooze, 
                 days, audio, enable 
                 FROM Alarms 
                 WHERE enable = False;
                 """
        self.cursor.execute(sql)
        recs = list()
        for r in self.cursor.fetchall() :
            d = {}
            d.update(r)
            recs.append(d)
        return recs

    def get_active_alarms(self) -> list:
        sql = """SELECT 
                 name, alarmtime, dura, snooze, 
                 days, audio, enable 
                 FROM Alarms 
                 WHERE enable = True;
                 """
        self.cursor.execute(sql)
        recs = list()
        for r in self.cursor.fetchall() :
            d = {}
            d.update(r)
            recs.append(d)
        return recs

    def get_alarm_by_date(self, date) -> list:
        sql = """SELECT 
               name, alarmtime, dura, snooze, 
               days, audio, enable 
               FROM Alarms 
               WHERE creationdate = '{}';
               """.format(date)
        self.cursor.execute(sql)
        recs = list()
        for r in self.cursor.fetchall() :
            d = {}
            d.update(r)
            recs.append(d)
        return recs

    def get_alarm_by_field(self, field: str, value) -> list:
        sql = """SELECT 
               name, alarmtime, dura, snooze, 
               days, audio, enable 
               FROM Alarms 
               WHERE {} = '{}';
               """.format(field, value)
        self.cursor.execute(sql)
        recs = list()
        for r in self.cursor.fetchall() :
            d = {}
            d.update(r)
            recs.append(d)
        return recs

#    def __concat(self,hour,min):
#        return "{:02}:{:02}".format(hour,min)

    def get_all(self) -> list:
        sql = """SELECT 
                 name, alarmtime, dura, snooze, 
                 days, audio, enable 
                 FROM Alarms;
                 """
        self.cursor.execute(sql)
        recs = list()
        for r in self.cursor.fetchall() :
            d = {}
            d.update(r)
            recs.append(d)
        return recs

    def close_conn(self) -> bool:
        try:
            self.conn.close()
            return True
#            logger.info("closeConn: Successfully closing DB connection")

        except Exception as e:
            return False
#            logger.error("Error Type : {}, Error Message : {}".format(type(e).__name__, e))
        
        return False



