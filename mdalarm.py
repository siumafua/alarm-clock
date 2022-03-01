import kivy
kivy.require('2.0.0')
from kivymd.app import MDApp
from kivy.uix.modalview import ModalView
from kivymd.uix.screen import MDScreen
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import ScreenManager
from kivy.core.audio import SoundLoader, Sound
from kivy.lang.builder import Builder
from alarmdata import AlarmData
from kivy.clock import Clock
from kivymd.uix.button import MDFillRoundFlatButton
from random import random
from time import strftime
from kivymd.uix.dialog import MDDialog
from datetime import datetime
from alarmop import AlarmOp
from kivymd.uix.filemanager import MDFileManager

from kivy.properties import (
    ObjectProperty,
    ListProperty,
    Property,
    NumericProperty,
    BooleanProperty,
)


class SelectRow(CheckBox):
    tag = Property('')
    selected = list()

    def on_press(self):
        if self.active:
            SelectRow.selected.append(self.tag)
        elif self.tag in SelectRow.selected:
            SelectRow.selected.remove(self.tag)
        print(SelectRow.selected)


class MainScreen(MDScreen):
    rv = ObjectProperty(None)
    selected = ListProperty([])
    dialog: MDDialog = ObjectProperty(MDDialog)
    tag = Property('')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.populate()

    def populate(self):
        db = AlarmData()
        data = db.get_all()
        db.close_conn()
        self.rv.data = []
        self.rv.data = data

    def btn_press(self, btn):
        self.tag = btn.text.lower()
        (Clock.create_trigger(self.btn_action, release_ref=False))()

    def btn_action(self, offset):
        match self.tag:
            case 'sort':
                self.rv.data = sorted(self.rv.data, key=lambda k: k['name'])
            case 'refresh':
                self.populate()
            case 'clear':
                self.rv.data = []
            case 'add':
                win = AlarmScreen()
                win.ids.sl_hour.value = 7
                win.ids.sl_min.value = 30
                win.ids.name.text = "alarm{}".format(str(random())[2:6])
                if app.config.get('Alarms', 'days') == 'None':
                    for d in win.repeat:
                        d.active = False
                else:
                    for d in win.repeat:
                        d.active = True
                win.ids.dura.text = "{:02}".format(int(app.config.get('Alarms', 'dura')))
                win.ids.snooze.text = "{:02}".format(int(app.config.get('Alarms', 'snooze')))
                win.ids.audio.text = app.config.get('Alarms', 'audio')
                win.ids.enable.active = bool(app.config.get('Alarms', 'enable'))
                win.open()

            case 'delete':
                if len(SelectRow.selected) < 1:
                    self.open_alert_dialog(
                        title="Operational error!",
                        text='You did not select any record(s). Please try again.',
                    )
                else:
                    self.open_yesno_dialog(
                        title="Do you want to continute?",
                        text="This will permanently remove these record(s) from the database.",
                        callback=self.delete_confirmation,
                    )

            case 'edit':
                if len(SelectRow.selected) < 1:
                    self.open_alert_dialog(
                        title="Operational error!",
                        text='You did not select any record(s). Please try again.',
                    )
                elif len(SelectRow.selected) > 1:
                    self.open_alert_dialog(
                        title="Operational error!",
                        text='Can only edit one record at a time. Please try again.',
                    )
                else:
                    db = AlarmData()
                    recs = (db.get_alarm_by_field('name', SelectRow.selected[0]))[0]
                    print("Edit")
                    print(recs)
                    db.close_conn()

                    win = AlarmScreen()
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

            case 'quit':
                app.stop()
            case _:
                print("Invalid button's tag: {}".format(self.tag))

    def open_alert_dialog(self, **kw):
        if 'title' not in kw.keys() or \
                'text' not in kw.keys():
            return

        self.dialog = MDDialog(
            title=kw['title'],
            text=kw['text'],
            buttons=[
                MDFillRoundFlatButton(
                    text="Ok",
                    text_color=app.theme_cls.primary_light,
                    on_release=self.close_alert_dialog,
                ),
            ],
        )
        self.dialog.open()

    def close_alert_dialog(self, btn):
        self.dialog.dismiss()

    def open_yesno_dialog(self, **kw):
        if 'title' or 'callback' \
                or 'text' not in kw.keys():
            return

        self.dialog = MDDialog(
            auto_dismiss=False,
            type="confirmation",
            title=kw['title'],
            text=kw['text'],
            buttons=[
                MDFillRoundFlatButton(
                    text="Yes",
                    text_color=app.theme_cls.primary_light,
                    on_release=kw['callback'],
                ),
                MDFillRoundFlatButton(
                    text="No",
                    text_color=app.theme_cls.primary_light,
                    on_release=kw['callback'],
                ),
            ],
        )
        self.dialog.open()

    def delete_confirmation(self, btn):
        if btn.text.lower() == 'yes':
            db = AlarmData()
            if db.del_records('name', SelectRow.selected):
                self.open_alert_dialog(
                    title="Information",
                    text="Record(s) with key: {} were deleted \
                        successfully".format(SelectRow.selected),
                )
            else:
                self.open_alert_dialog(
                    title="Error Message",
                    text="Error deleting records: {}. \
                        Please check log then try again.".format(SelectRow.selected),
                )
        self.dialog.dismiss()


class RepeatCheckBox(CheckBox):
    pass


class AlarmScreen(ModalView):
    repeat = ListProperty(None)
    enable = ObjectProperty(None)
    manager_open = BooleanProperty(False)
    tag = Property('')
    days = ListProperty([
        'Mon', 'Tue', 'Wed',
        'Thu', "Fri", 'Sat',
        'Sun'
    ])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audio = ''
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            size_hint=(.9, .8),
            ext=['.mp3', '.wav', 'mp4']
        )

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
                    'name': self.ids.name.text,
                    'alarmtime': self.ids.time.text,
                    'dura': int(self.ids.dura.text),
                    'snooze': int(self.ids.snooze.text),
                    'days': select_days,
                    'audio': self.ids.audio.text,
                    'enable': 1 if self.enable.active else 0,
                }

                db = AlarmData()
                res = db.get_alarm_by_field('name', self.ids.name.text)
                if len(res) >= 1:  # key existed, Update
                    db.update_record('name', rec)
                else:  # insert
                    if db.insert_record(rec):
                        app.main_screen.open_alert_dialog(
                            title="Information!",
                            text="Record \"{}\" were added successfully".format(rec),
                        )
                    else:
                        app.main_screen.open_alert_dialog(
                            title="Error Message!!",
                            text="Error saving record \"{}\". Please check log \
                                then try again".format(rec),
                        )
                db.close_conn()
                self.dismiss()
                app.main_screen.populate()  # reload alarm data from database
                app.alarmop.refresh(0)  # reload monitored alarms

            case 'reset':
                self.ids.name.text = "alarm{}".format(str(random())[2:6])
                self.ids.sl_hour.value = 7
                self.ids.sl_min.value = 30
                if app.config.get('Alarms', 'days') == 'None':
                    for d in self.repeat:
                        d.active = False
                else:
                    for d in self.repeat:
                        d.active = True
                self.ids.dura.text = "{:02}".format(int(app.config.get('Alarms', 'dura')))
                self.ids.snooze.text = "{:02}".format(int(app.config.get('Alarms', 'snooze')))
                self.ids.audio.text = app.config.get('Alarms', 'audio')
                self.ids.enable.active = bool(app.config.get('Alarms', 'enable'))

            case 'cancel':
                self.dismiss()
            case 'browse':
                self.file_manager_open()
            case _:
                print("Invalid button's tag: {}".format(self.tag))

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


class AlarmView(ModalView):
    alarm_audio = ObjectProperty()
    pause = BooleanProperty(False)
    nloop = NumericProperty(0)

    def __init__(self, **kwargs):
        if 'audio' and 'dura' and 'snooze' in kwargs.keys():
            self.audio = kwargs['audio']
            self.dura = kwargs['dura']
            self.snooze = kwargs['snooze']
            del kwargs['audio']
            del kwargs['dura']
            del kwargs['snooze']
            self.auto_dismiss = False
        super().__init__(**kwargs)

    def open(self, *largs, **kwargs):
        super().open(*largs, **kwargs)
        self.start_alarm()

    def start_alarm(self):
        self.ids.pause.disabled = False
        self.ids.resume.disabled = True
        self.alarm_audio = SoundLoader.load(self.audio)
        if self.alarm_audio.state != 'stop':
            self.alarm_audio.stop()
        self.nloop = self.dura * 60 / self.alarm_audio.length
        self.alarm_audio.loop = False
        self.alarm_audio.bind(on_stop=self.stopping)
        self.alarm_audio.bind(on_play=self.playing)
        self.alarm_audio.play()

    def set_volume(self, val):
        self.alarm_audio.volume = val

    def playing(self, obj):
        print("playing ")

    def stopping(self, obj):
        """stopping - Called when alarm stop playing.

        if not pause and nloop > 0
            keep restart the alarm

        Args:
            obj : ignored
        """
        if not self.pause:
            if self.nloop > 0:
                if self.alarm_audio.state != 'stop':
                    self.alarm_audio.stop()
                self.alarm_audio.play()
                self.nloop -= 1

    def stop_alarm(self, btn):
        if self.alarm_audio.state != 'stop':
            self.alarm_audio.stop()
        self.alarm_audio.unload()
        app.alarm_start = False
        self.dismiss()

    def pause_alarm(self, btn):
        self.ids.pause.disabled = True
        self.ids.resume.disabled = False
        self.pause = True
        self.alarm_audio.stop()

    def resume_alarm(self, btn):
        self.ids.pause.disabled = False
        self.ids.resume.disabled = True
        self.pause = False
        self.stopping(None)


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
        # 'window_icon':
        # ‘trace’, ‘debug’, ‘info’, ‘warning’, ‘error’ or ‘critical’
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
