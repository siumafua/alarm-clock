from kivy.logger import Logger
import sqlite3
from functools import singledispatchmethod

class AlarmData:
    """AlarmDate - Alarms database.

    A simple class to manage a database that stores the user's alarms_data.
    The database has a at least one table. This class take care of 
    operations like:
        creating the alarms table: (alarms)
        insert alarm new alarm 
        update alarms details (duration, snooze, audio file, etc)
        delete alarms
        retrieve alarms (all or based on specified condition)
        
    """
    
    def __init__(self, 
                 table="Alarms", 
                 dbname = "resources/alarm.db"):
        self.conn = sqlite3.connect(dbname)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.table = table

    @property
    def is_exists(self) -> bool:
        """is_exists Check if the alarms tables existed.

        Readonly property. Identify if the alarm table exists. 
                
        Return: true if exists otherwise false.
        """
        
        try:
            self.cursor.execute("SELECT count(name) FROM sqlite_master \
                WHERE type='table' AND name='{}'".format(self.table))
            return True \
                if self.cursor.fetchone()[0] == 1 else \
                   False 
        except Exception as e:
            Logger.exception("is_table_exists: Error Type : {}, Error Message : {}".format(type(e).__name__, e))
        return False

    
    def create_alarms_table(self) -> int:
        """create_alarms_table Create alarm(s) table.
        
        Creating the alarms tables. The table fields are
        shown below. 
            rid - unique id for each record 
            name - alarm name or description like 'work alarm', etc.
            alarmtime - time of the alarm 8:30, 9:00 - time in 24hrs
            dura int - duration, i.e how long the alarm ring for 
            snooze - pause between each ring
            days text - days of the week this alarm is active on 
            audio text - full path to alarm audio file to play (.mp3 or .wav)  
            enable bool - this alarm state, enabled or disabled.
        
        Return: 1 if successful, 0 or -1 depending on error type
        """
        
        try:
            sql = """ 
                CREATE TABLE Alarms 
                    (creationdate text, 
                     rid text primary key,
                     name text, 
                     alarmtime text, 
                     dura int, 
                     snooze int, 
                     days text, 
                     audio text, 
                     enable bool);
            """
            self.cursor.execute(sql)
            Logger.info('create_alarms_table: Successfully created Alarm table')
            return 1
        except sqlite3.OperationalError as o:
            Logger.exception("create_alarms_table: Exception : {}, Error Message : {}".format(type(o).__name__, o))
            return -1
        except Exception as e:
            Logger.exception("create_alarms_table: Exception : {}, Error Message : {}".format(type(e).__name__, e))
            return 0

    def del_records(self, field: str, values: list) -> bool:
        """del_records delete alarm(s) records

        Delete from the alarms table one or more records. 
        Records are selected based on a field value

        Keyword arguments:
            field (str): field
            values (list): field values

        Examples: 
        del_records('rid',['alarm1','alarm2']) will
            delete all records with rid == 'alarm1' and rid == 'alarm2'
        
        Returns:
            bool: success or failure
        """
        
        n = len(values)
        sql = "DELETE FROM Alarms WHERE {} = '{}' ".format(field, values[0])
        for x in range(1, n - 1):
            sql = sql + "OR '{}' ".format(values[x])
        sql = sql + "OR '{}'".format(values[n-1])
        print("sql :" + sql)
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            Logger.info("del_records: Successfully delete records with \
                values ({}) for fields {}".format(values, field))
            return True
        except sqlite3.OperationalError as o:
            Logger.exception("del_records: Exception : {}, Error Message : {}".format(type(o).__name__, o))
        except Exception as e:
            Logger.exception("del_records: Exception : {}, Error Message : {}".format(type(e).__name__, e))
        return False

    def drop_table(self) -> bool:
        """drop_table Delete alarms table.

        This will delete all alarms records.

        Returns:
            bool: success or failure
        """
        
        try:
            self.cursor.execute("DROP TABLE Alarms;")
            self.conn.commit()
            Logger.info("dropTable: Successfully delete Alarms table")
            return True
        except sqlite3.OperationalError as o:
            Logger.exception("drop_table: Exception : {}, Error Message : {}".format(type(o).__name__, o))
        except Exception as e:
            Logger.exception("drop_table: Exception : {}, Error Message : {}".format(type(e).__name__, e))
        return False

    @singledispatchmethod
    def update_record(self) -> bool:
        """update_record Update an alarm record.

        Overloaded function for updating an alarm record.
        
        Raises:
            NotImplementedError: this base function is not impletmented
                actual function implementations are detailed below 
        """
        raise NotImplementedError("Error: Overloaded method has not being impletmented.")

    @update_record.register
    def _(self, rec: tuple) -> bool:
        """update_record Update an alarm record.

        This version of update_record, update only one field 
        identified by the rid field which included in the tuple
        
        Args:
            rec (tuple): (rid, field, value) 
                rid - rid of record to update
                field - field to update
                value - field new value
                         
        Returns:
            bool: success or failure
        """

        # minimum 3 params provided
        if(len(rec) == 3):
            if type(rec[2])==str:
                sql = "UPDATE Alarms SET {}='{}' WHERE rid ='{}'".\
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
        Logger.info("update_record: sql statement: {}".format(sql))

        try:
            self.cursor.execute(sql) 
            self.conn.commit()
            Logger.info("update_record: successfully updating record with: {}".format(rec))
            return True
        except sqlite3.OperationalError as o:
            Logger.exception("update_record: Exception : {}, Error Message : {}".format(type(o).__name__, o))
        except Exception as e:
            Logger.exception("update_record: Exception : {}, Error Message : {}".format(type(e).__name__, e))
        return False


    @update_record.register
    def _(self, key: str, rec: dict) -> bool:
        """update_record Update alarm record.

        This version accept a key (field) which identified the record to update. 
        The new record (including the rid field) is send as dictionary

        Args:
            key (str): field name- record key
            rec (dict): new record details

        Returns:
            bool: success or failure
        """
        
        if len(rec) < 1:
            return False

        sql ="UPDATE Alarms SET "
        for k,v in rec.items():
            if k != key and k != 'date': 
                if k in ('id', 'name','alarmtime','audio','days'):
                    sql = "{}{} = \'{}\',".format(sql, k, v)
                else:
                    sql = "{}{} = {},".format(sql, k, int(v))

        sql = "{} WHERE {} = '{}'".format(sql[:len(sql)-1], key, rec[key])
        Logger.info("update_record: sql statement: {}".format(sql))

        try:
            self.cursor.execute(sql) 
            self.conn.commit()
            Logger.info("update_record: successfully updating record with: {}".format(rec))
            return True
        except sqlite3.OperationalError as o:
            Logger.exception("update_record: Exception : {}, Error Message : {}".format(type(o).__name__, o))
        except Exception as e:
            Logger.exception("update_record: Exception : {}, Error Message : {}".format(type(e).__name__, e))
        return False


    @singledispatchmethod
    def insert_record(self, rec) -> bool:
        raise NotImplementedError("Error: Overloaded method has not being impletmented.")

    @insert_record.register
    def _(self, rec: dict) -> bool:
        """insert_record (Overload) insert a new record

        Insert a new record. Record is specified using a dict.

        Keyword arguments:
            rec (dict): new record to insert

        Returns:
            bool: success or failure
        """

        v = tuple(rec.values())
        
        # construct (?,?,?...)
        s = "?, " * len(rec.keys())
        s = "({})".format(s[:len(s)-2]) #remove trailing comma
        
        # construct the sql statement
        sql="INSERT INTO Alarms VALUES "
        sql = sql + "{}".format(s)        
        Logger.info("insert_record: sql statement: {}".format(sql))

        try:
            self.cursor.execute(sql, v) 
            self.conn.commit()
            Logger.info("insert_record: successfully adding {}".format(rec))
            return True
        except sqlite3.OperationalError as o:
            Logger.exception("insert_record: Exception Type : {}, Error Message : {}".format(type(o).__name__, o))
        except Exception as e:
            Logger.exception("insert_record: Exception Type : {}, Error Message : {}".format(type(e).__name__, e))
        return False

    @insert_record.register
    def _(self, rec: tuple) -> bool:
        """insert_record - Insert new record

        This version of the method accept new record as tuple.

        Keyword arguments:
            rec (tuple): new record to insert
                format: (creationdate, rid, name, 
                            alarmtime, dura, snooze, days, audio, enable)
        Returns:
            bool: success or failure
        """

        try:
            sql = """
                   INSERT 
                   INTO Alarms 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                   """
            self.cursor.execute(sql, rec) 
            self.conn.commit()
            Logger.info("insert_record: successfully adding {}".format(rec))
            return True
        
        except sqlite3.OperationalError as o:
            Logger.exception("insert_record: Exception Type : {}, Error Message : {}".format(type(o).__name__, o))
        except Exception as e:
            Logger.exception("insert_record: Exception Type : {}, Error Message : {}".format(type(e).__name__, e))
        return False
    
    @property
    def inactive_alarms(self) -> list:
        """inactive_alarms Get a list of inactive alarms.

        read-only property - return a list of all inactive alarms in
            the database
                      
        Return: 
            (list of dict): alarm records that's disabled
        """
        
        sql = """SELECT 
                 rid, name, alarmtime, dura, snooze, 
                 days, audio, enable 
                 FROM Alarms 
                 WHERE enable = False;
                 """
        try:
            self.cursor.execute(sql)
            recs = list()
            for r in self.cursor.fetchall() :
                d = {}
                d.update(r)
                recs.append(d)
            return recs
        except sqlite3.OperationalError as o:
            Logger.exception("get_inactive_alarms: Exception Type : {}, Error Message : {}".format(type(o).__name__, o))
            return list()
        except Exception as e:
            Logger.exception("get_inactive_alarms: Exception Type : {}, Error Message : {}".format(type(e).__name__, e))
            return list()
    
    @property
    def active_alarms(self) -> list:
        """active_alarms Get a list of active alarms

        read-only property - return a list of all active alarms.
                
        Return:
            (list of dict): alarm records that are active
        """
        
        sql = """SELECT 
                 rid, name, alarmtime, dura, snooze, 
                 days, audio, enable 
                 FROM Alarms 
                 WHERE enable = True;
                 """
        try:
            self.cursor.execute(sql)
            recs = list()
            for r in self.cursor.fetchall() :
                d = {}
                d.update(r)
                recs.append(d)
            return recs
        except sqlite3.OperationalError as o:
            Logger.exception("get_active_alarms: Exception Type : {}, Error Message : {}".format(type(o).__name__, o))
        except Exception as e:
            Logger.exception("get_active_alarms: Exception Type : {}, Error Message : {}".format(type(e).__name__, e))
        return list()

    
    def get_alarm_by_date(self, date) -> list:
        """get_alarm_by_date Get a list alarms created at specified date
        
        Keyword arguments:
            date (datetime): records' date 

        Example: 
            get_alarm_by_date('21-04-2022') would result in
                sql = "Select <fields> from <alarm-table> where creationdate = '21-04-2022'"
                which returns
                [{'creationdate':'21-04-2022',...},
                 {'creationdate':'21-04-2022',...},
                 ...]            
        Return:
            (list of dict): alarm(s) created on given date or empty list
                if record(s) not found.
        """
        
        sql = """SELECT 
               rid, name, alarmtime, dura, snooze, 
               days, audio, enable 
               FROM Alarms 
               WHERE creationdate = '{}';
               """.format(date)
        try:
            self.cursor.execute(sql)
            recs = list()
            for r in self.cursor.fetchall() :
                d = {}
                d.update(r)
                recs.append(d)
            return recs
        except sqlite3.OperationalError as o:
            Logger.exception("get_alarms_by_date: Exception Type : {}, Error Message : {}".format(type(o).__name__, o))
            return list()
        except Exception as e:
            Logger.exception("get_alarms_by_date: Exception Type : {}, Error Message : {}".format(type(e).__name__, e))
            return list()
    
    def get_alarm_by_field(self, field: str, value) -> list:
        """get_alarm_by_field Get a list alarms with specified field's value
        
        Keyword arguments:
            field (str): field name
            value (any): field's value 
                        
        Example:
        get_alarm_by_field('id', 'alarm1') returns
        record(s) with rid == 'alarm1'

        Return:
            (list of dict): alarm records with specified field value
        """

        sql = """SELECT 
               rid, name, alarmtime, dura, snooze, 
               days, audio, enable 
               FROM Alarms 
               WHERE {} = '{}';
               """.format(field, value)
        try:
            self.cursor.execute(sql)
            recs = list()
            for r in self.cursor.fetchall() :
                d = {}
                d.update(r)
                recs.append(d)
            return recs
        except sqlite3.OperationalError as o:
            Logger.exception("get_alarms_by_field: Exception Type : {}, Error Message : {}".format(type(o).__name__, o))
            return list()
        except Exception as e:
            Logger.exception("get_alarms_by_field: Exception Type : {}, Error Message : {}".format(type(e).__name__, e))
            return list()

    @property
    def alarms(self) -> list:
        """alarms Get all alarms records
        
        Return: 
            (list-of-dict): list of all alarms record. Each record is a dict
        """
        
        sql = """SELECT 
                 rid, name, alarmtime, dura, snooze, 
                 days, audio, enable 
                 FROM Alarms;
                 """
        try:
            self.cursor.execute(sql)
            recs = list()
            for r in self.cursor.fetchall() :
                d = {}
                d.update(r)
                recs.append(d)
            return recs
        except sqlite3.OperationalError as o:
            Logger.exception("get_all: Exception Type : {}, Error Message : {}".format(type(o).__name__, o))
            return list()
        except Exception as e:
            Logger.exception("get_all: Exception Type : {}, Error Message : {}".format(type(e).__name__, e))
            return list()


    def close_conn(self) -> bool:
        """close_conn Close database connection

        Returns:
            bool: success or failure
        """
        try:
            self.conn.close()
            Logger.info("closeConn: Successfully closing DB connection")
            return True
        except Exception as e:
            Logger.exception("close_conn: Error Type : {}, Error Message : {}".format(type(e).__name__, e))
        return False



