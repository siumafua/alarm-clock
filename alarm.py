
#  2
# sudo update-alternatives --config python3sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10

import logging
from os import path
from logging import config

log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
print(log_file_path)
config.fileConfig(log_file_path)
logger = logging.getLogger(__name__)

# ----------------------

#from kivy.app import App
from kivymd.app import MDApp
from kivy.uix.boxlayout  import BoxLayout
from kivy.uix.popup  import Popup
from kivy.uix.label  import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from alarmdata import AlarmData

########################################################################

# creating the root widget used in .kv file
class AlarmLayout(BoxLayout):
    """
    AlarmLayout(BoxLayout) app main layout. 
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.content = self.ids.content
        lbl = Label(text = 'Content')
        lbl.font_size = '16sp'
        lbl.color = (0, 0, 0)
        self.content.add_widget(lbl)

    def delete_alarm(self):
        pass

    def edit_alarm(self):
        pass


class AlarmPopup(Popup):
    """
    MyPopup popup window for adding new alarm. 
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.days = {'Mon':0, 'Tues':0, 'Wed':0, 'Thur':0, 'Fri':0, 'Sat':0, 'Sun':0}
        self.repeat = self.ids.repeat

        """ 
        Create 7 labels and 7 checkboxes in two rows
        """
        for day in self.days:
            lbl = Label(text=day)
            lbl.font_size = '12sp'
            lbl.color = (0, 0, 0)
            self.repeat.add_widget(lbl)
            
        for day in self.days:
            chk = CheckBox()
            chk.size_hint_y = None
            chk.height = '48dp'
            chk.color = (0, 0, 0)
            chk.id = day
            chk.bind(on_press=self.check_press) 
            self.repeat.add_widget(chk)


    """ 
    Functions: incre_min incre_hour decre_min decre_hour.
    
    Increment/decrement hours and minute value.

    """
    def incre_min(self):
        self.ids.timin.text = self.__incre_textval(self.ids.timin.text)

    def decre_min(self):
        self.ids.timin.text = self.__decre_textval(self.ids.timin.text)

    def incre_hour(self):
        self.ids.tihour.text = self.__incre_textval(self.ids.tihour.text, 24)

    def decre_hour(self):
        self.ids.tihour.text = self.__decre_textval(self.ids.tihour.text, 24)
        
# --- handle events

    def check_press(self, obj):
        """
        check_press update days according to checkboxes' values
        """
        for day in self.days:
            if( obj.id == day):
                self.days[day] = 1 - self.days[day] 

    def add_alarm(self):
        """
        add_alarm adding new alarm
        """
        print(self.ids.tihour.text)
        print(self.ids.timin.text)
        print(self.ids.snooze.text)
        print(self.ids.dura.text)
        print(self.ids.name.text)
        print(self.ids.audio.text)
        print(self.ids.repeat.days)

        days = self.ids.repeat.days
        dstr = ""
        for d in days:
            if days[d] ==  1:
                dstr = dstr + ",{}".format(d)
                days[d] = 0
        print(dstr)
        data = AlarmData()
        print(data)
        self.dismiss()



# --- private functions
    def __incre(self, x):
        return lambda n : 0 if (n + 1) >= x  else (n + 1)

    def __decre(self, x):
        return lambda n : x - 1 if (n - 1) < 0  else (n - 1)

    def __incre_textval(self, vstr, vmax = 60):
        func = self.__incre(vmax)
        v = func(int(vstr))
        return "0" + str(v) if(v < 10) else str(v)

    def __decre_textval(self, vstr, vmax = 60):
        func = self.__decre(vmax)
        v = func(int(vstr))
        return "0" + str(v) if(v < 10) else str(v)

# --- end private functions        

class AlarmApp(MDApp):
    def build(self): 
        return AlarmLayout()

# creating object of Multiple_LayoutApp() class
if __name__ == '__main__':
    logger.info("running main")
    myalarm = AlarmApp()
    myalarm.run()
