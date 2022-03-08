import kivy
kivy.require('2.0.0')
from kivymd.app import MDApp
from kivy.uix.modalview import ModalView
from kivymd.uix.screen import MDScreen
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import ScreenManager
from kivy.core.audio import SoundLoader, Sound
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivymd.uix.button import MDFillRoundFlatButton, MDFlatButton
from random import random
from time import strftime
from datetime import datetime
from alarmop import AlarmOp
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel

from kivy.properties import (
    ObjectProperty,
    ListProperty,
    Property,
    NumericProperty,
    BooleanProperty,
    StringProperty,
)

from alarmdata import AlarmData
from alarmsnackbar import AlarmSnackbar
from newalarm import NewAlarm
from alarmview import AlarmView

class SelectRow(CheckBox):
   
    tag = StringProperty('')
    selected = list()

    def on_release(self) -> None:
        if self.tag == 'all':
            print("all here")
            for cb in app.main_screen.ids.rv.ids:
                print(cb)
            return
        if self.active:
            SelectRow.selected.append(self.tag)
        elif self.tag in SelectRow.selected:
            SelectRow.selected.remove(self.tag)
        print(SelectRow.selected)


class MainScreen(MDScreen):
    
    rv = ObjectProperty(None)
    selected = ListProperty(None)
    dialog = ObjectProperty(None)
    tag = Property('')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.populate()

    def populate(self):
        db = AlarmData()
        data = db.alarms
        db.close_conn()
        self.rv.data = []
        self.rv.data = data
       
    def btn_press(self, btn):
        self.tag = btn.text.lower()
        (Clock.create_trigger(self.btn_action, release_ref=False))()
        self.tag = ''

    def btn_action(self, offset):
        match self.tag:
            case 'sort':
                self.rv.data = sorted(self.rv.data, key=lambda k: k['rid'])
            case 'refresh':
                self.populate()
            case 'clear':
                self.rv.data = []
            case 'add':
                win = NewAlarm(app=app)
                win.ids.sl_hour.value = 7
                win.ids.sl_min.value = 30
                win.ids.rid.text = "alarm{}".format(str(random())[2:6])
                win.ids.name.text = ""
                for cb in win.repeat:
                    cb.active = False if \
                        app.config.get('Alarms', 'days') == 'None'\
                           else True
                win.ids.dura.text = "{:02}".format(int(app.config.get('Alarms', 'dura')))
                win.ids.snooze.text = "{:02}".format(int(app.config.get('Alarms', 'snooze')))
                win.ids.audio.text = app.config.get('Alarms', 'audio')
                win.ids.enable.active = bool(app.config.get('Alarms', 'enable'))
                win.open()
            case 'delete':
                if len(SelectRow.selected) < 1:
                    AlarmSnackbar.info(msg='ERROR: Please select select record(s) to delete.',
                                       icon="alert-circle")
                else:
                    def del_yes():
                        db = AlarmData()
                        print(SelectRow.selected)
                        if db.del_records('rid', SelectRow.selected):
                            AlarmSnackbar.info(msg="Record(s) with key: {} were deleted \
                                    successfully".format(SelectRow.selected))
                        else:
                            AlarmSnackbar.info(msg="ERROR: Deleting records failed: {}. \
                                    Please check log or contact admin for help.".format(SelectRow.selected),
                                       icon="alert-circle")
                        db.close_conn()
                        
                    def del_no():
                        sb.dismiss()
            
                    sb = AlarmSnackbar.alert(
                        msg="Do you want to continute?",
                        ybtn=('del_y', del_yes),
                        nbtn=('del_n', del_no))
                    self.selected = []
            case 'edit':
                if len(SelectRow.selected) < 1:
                    AlarmSnackbar.info(msg="ERROR: Please select a record to edit.",
                                       icon="alert-circle")
                elif len(SelectRow.selected) > 1:
                    AlarmSnackbar.info(msg='ERROR: You can only edit one record at a time.',
                                       icon="alert-circle")
                else:
                    db = AlarmData()
                    recs = (db.get_alarm_by_field('rid', SelectRow.selected[0]))[0]
                    db.close_conn()

                    win = NewAlarm(app=app)
                    win.ids.rid.text = recs['rid']
                    win.ids.name.text = recs['name']
                    hr, mn = recs['alarmtime'].split(':')
                    win.ids.sl_hour.value = int(hr)
                    win.ids.sl_min.value = int(mn)

                    for day in list(map(lambda x: (x.lower()).replace(" ", ""), \
                                        recs['days'].split(','))):
                        win.ids[day].active = 1
                    win.ids.dura.text = "{:02}".format(recs['dura'])
                    win.ids.snooze.text = "{:02}".format(recs['snooze'])
                    win.ids.audio.text = recs['audio']
                    win.ids.enable.active = recs['enable']
                    win.open()
                self.selected = []
            case 'quit':
                AlarmSnackbar.info("App shutting down...")
                app.stop()
            case _:
                AlarmSnackbar.info("Invalid button's tag: {}".format(self.tag))


class MDAlarmApp(MDApp):
    
    start_update = NumericProperty(0)
    alarm_start = BooleanProperty(False)
    alarmop = ObjectProperty()
    sm = ObjectProperty()
    main_screen = ObjectProperty()

    def update_title(self, nap):
        self.title = "Simple Alarm Clock : {}".format(strftime("%a %b %Y %H:%M:%S"))
        self.use_kivy_settings = True

    def monitor_alarm(self, nap):
    
        alarm = self.alarmop.monitor_alarm()
        if len(alarm) > 0:
            if not self.alarm_start:
                self.alarm_start = True
                av = AlarmView(audio=alarm['audio'],
                               dura=alarm['dura'], snooze=['snooze'])
                av.open()

    def on_start(self):

        self.alarmop = AlarmOp()
        (Clock.create_trigger(callback=self.monitor_alarm, timeout=1.0, interval=True, release_ref=False))()
        (Clock.create_trigger(callback=self.update_title, timeout=0.0, interval=True, release_ref=False))()
        # Clock.schedule_interval(self.win.update_time, 0)
        return super().on_start()

    def build(self):

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "BlueGray"

        Builder.load_file("kv/main_screen.kv")
        Builder.load_file("kv/alarm_screen.kv")
        Builder.load_file("kv/dialog.kv")

        self.main_screen = MainScreen(name='main')
        self.sm = ScreenManager()
        self.sm.add_widget(self.main_screen)
        return self.sm

    def build_config(self, config):
        config.setdefaults('Alarms', {
            'audio': 'resources/default.mp3',
            'days': 'None',
            'dura': 5,
            'snooze': 5,
            'enable': 1
        })

    def build_settings(self, settings):
        json_data = """[
         {"type": "string",
          "title": "Alarm audio file",
          "desc": "Default alarm audio file",
          "section": "Alarms",
          "key": "audio"},
         {"type": "options",
          "title": "Alarm days",
          "desc": "Default alarm days",
          "section": "Alarms",
          "key": "days",
          "options": ["None", "All"]},
         {"type": "numeric",
          "title": "Duration",
          "desc": "Default alarm duration (mins)",
          "section": "Alarms",
          "key": "dura"},          
         {"type": "numeric",
          "title": "Snooze",
          "desc": "Default alarm snooze period (mins)",
          "section": "Alarms",
          "key": "snooze"},
         {"type": "options",
          "title": "Enable",
          "desc" : "Default alarm state (enable/disable)",
          "section": "Alarms",
          "key": "enable",
          "options": ["True", "False"]}]
        """
        settings.interface.menu.width = '100dp'
        settings.add_json_panel('Alarm application',
                                self.config, data=json_data)

    def on_config_change(self, config, section, key, value):
        if config is self.config:
            token = (section, key)
            if token == ('Alarms', 'audio'):  # update database
                rec = (key, value)
                db = AlarmData()
                if not db.update_record(rec):
                    self.main_screen.open_alert_dialog(
                        title="Error message!",
                        text="""Config change \"{}\" but updating database failed 
                                Check log for details.
                            """.format(rec), )
                db.close_conn()
        return super().on_config_change(config, section, key, value)


if __name__ == "__main__":
    app = MDAlarmApp()
    app.run()

"""
    config.setdefaults('kivy', {
        'desktop': 1,
        'log_dir': 'string',
        'log_enable': 1,
        'log_level':   'info',
        'log_name': 'string',
        'log_maxfiles': 20,
    })
"""
