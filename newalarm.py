import kivy
kivy.require('2.0.0')
from kivy.uix.modalview import ModalView
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock
from random import random
from datetime import datetime
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel

from kivy.properties import (
    ObjectProperty,
    ListProperty,
    Property,
    BooleanProperty,
)

from alarmdata import AlarmData
from alarmsnackbar import AlarmSnackbar

class NewAlarm(ModalView):
    
    repeat = ListProperty([])
    enable = ObjectProperty(None)
    manager_open = BooleanProperty(False)
    tag = Property('')
    days = ListProperty([
        'Mon', 'Tue', 'Wed',
        'Thu', "Fri", 'Sat',
        'Sun'
    ])

    def __init__(self, **kwargs):
        if 'app' in kwargs.keys():
            self.app = kwargs['app']
            del kwargs['app']
        
        super().__init__(**kwargs)
        self.audio = ''
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            size_hint=(.9, .8),
            ext=['.mp3', '.wav', 'mp4']
        )
        
        for d in self.days:
            self.ids.repeat_box.add_widget(MDLabel(
                text=d, 
                font_style='Caption',
                halign = "right",
                ))
            cb = CheckBox(
                    active = False,
                    color = (0, 0, 0, 1),
                )
            cb.id = d.lower()
            self.repeat.append(cb)
            self.ids.repeat_box.add_widget(cb)
            
 
    def btn_press(self, btn):
        self.tag = btn.text.lower()
        (Clock.create_trigger(self.btn_action, release_ref=False))()

    def btn_action(self, offset):
        match self.tag:
            case 'save':  # add or update
                select_days = ''
                for x in range(0, len(self.repeat)):
                    if self.repeat[x].active:
                        select_days = "{},{}".format(select_days, self.days[x])
                select_days = select_days[1:]

                rec = {
                    'date': datetime.now().strftime("%d-%m-%Y"),
                    'rid' : self.ids.rid.text,
                    'name': self.ids.name.text,
                    'alarmtime': self.ids.time.text,
                    'dura': int(self.ids.dura.text),
                    'snooze': int(self.ids.snooze.text),
                    'days': select_days,
                    'audio': self.ids.audio.text,
                    'enable': 1 if self.enable.active else 0,
                }

                db = AlarmData()
                res = db.get_alarm_by_field('rid', self.ids.rid.text)
                if len(res) >= 1:  # key existed, Update
                    if db.update_record('rid', rec):
                        AlarmSnackbar.info(
                            msg="Record \"{}\" were updated successfully".format(rec),
                            icon="information"
                        )
                else:  # insert
                    if db.insert_record(rec):
                        AlarmSnackbar.info(
                            msg="Record \"{}\" were added successfully".format(rec),
                            icon="information"
                        )
                    else:
                        AlarmSnackbar.info(
                            msg="Error saving record \"{}\". Please check log \
                                then try again".format(rec),
                            icon="alert-circle",
                        )
                db.close_conn()
                self.dismiss()
                self.app.main_screen.populate()  # reload alarm data from database
                self.app.alarmop.refresh(0)  # reload monitored alarms

            case 'reset':
                self.ids.rid.text = "alarm{}".format(str(random())[2:6])
                self.ids.name.text = ""
                self.ids.sl_hour.value = 7
                self.ids.sl_min.value = 30
                if self.app.config.get('Alarms', 'days') == 'None':
                    for d in self.repeat:
                        d.active = False
                else:
                    for d in self.repeat:
                        d.active = True
                self.ids.dura.text = "{:02}".format(int(self.app.config.get('Alarms', 'dura')))
                self.ids.snooze.text = "{:02}".format(int(self.app.config.get('Alarms', 'snooze')))
                self.ids.audio.text = self.app.config.get('Alarms', 'audio')
                self.ids.enable.active = bool(self.app.config.get('Alarms', 'enable'))

            case 'cancel':
                self.dismiss()
            case 'browse':
                self.file_manager_open()
            case _:
                AlarmSnackbar.info(msg="Invalid button's tag: {}".format(self.tag))

    def file_manager_open(self):
        self.file_manager.show('.')  # output manager to the screen
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        self.audio = path
        app.config.set('Alarms', 'audio', path)

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()
