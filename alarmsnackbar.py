import kivy
kivy.require('2.0.0')
from kivymd.uix.snackbar import BaseSnackbar
from kivy.core.window import Window

from kivy.properties import (
    ObjectProperty,
    ListProperty,
    Property,
    NumericProperty,
    BooleanProperty,
    StringProperty,
)

class InfoSnackbar(BaseSnackbar):
    text = StringProperty(None)
    icon = StringProperty(None)
    font_size = NumericProperty("15sp")

class YesnoSnackbar(BaseSnackbar):
    text = StringProperty(None)
    icon = StringProperty(None)
    font_size = NumericProperty("15sp")
    
    # yes and no buttons & buttons' tags
    yes = ObjectProperty(None)
    no = ObjectProperty(None)   
    tags = ListProperty(None)
    
    # list of tags an associated callbacks
    # keep the yes and no buttons' list seprately for 
    # simplicity sake
    
    def __init__(self, **kwargs):
        if 'ytag' and 'ntag' in kwargs.keys():
            self.tags = list((kwargs['ytag'], kwargs['ntag']))
            del kwargs['ytag']
            del kwargs['ntag']
            super().__init__(**kwargs)    
        else:
            raise SyntaxError("Missing 'ytag' or 'ntag' or both, arguments")
        
        # Call super to setup the buttons
        # before set the tags otherwise it will throw an exception
        self.yes.tag = self.tags[0]
        self.no.tag = self.tags[1]
        self.yfunc = list()
        self.nfunc = list()
    
    def setup_ycbs(self, tag, cb=None):
        
        if cb is None:
            for tp in self.yfunc:
                if tp[0] == tag:
                    self.yfunc.remove(tp)
        else:
            self.yfunc.append((tag, cb))
            
    def setup_ncbs(self, tag, cb=None):
        if cb is None:
            for tp in self.nfunc:
                if tp[0] == tag:
                    self.nfunc.remove(tp)
        else:
            self.nfunc.append((tag, cb))
            
    def press_yes(self, btn):
        for tag, cb in self.yfunc:        
            if btn.tag == tag:
                cb()
        
    def press_no(self, btn):
        for tag, cb in self.nfunc:        
            if btn.tag == tag:
                cb()
        
        
class AlarmSnackbar:

    @staticmethod
    def info(msg: str, icon: str = 'information-circle'):
        
        # Info snackbar 
        snackbar = InfoSnackbar(
            text=msg,
            icon=icon,
            duration=4
        )
        # setup dynamic width
        snackbar.size_hint_x = (
            Window.width - (snackbar.snackbar_x * 2)
        ) / Window.width
        # show the snackbar
        snackbar.open()

       
    @staticmethod
    def alert(msg: str, ybtn: tuple, nbtn: tuple, icon: str = "alert"):
        
        # Alert snackbar with 2 buttons, duration change from 3 to 6
        # and no auto_dismiss.
        snackbar = YesnoSnackbar(
            text=msg,
            icon=icon,
            duration=6,
            auto_dismiss = False,
            ytag=ybtn[0],
            ntag=nbtn[0],
        )
        
        # setup tag and callbacks
        snackbar.setup_ycbs(*ybtn)
        snackbar.setup_ncbs(*nbtn)
        
        # dynamic snackbar width to match parent window's width
        snackbar.size_hint_x = (
            Window.width - (snackbar.snackbar_x * 2)
        ) / Window.width
        # show the Snackbar
        snackbar.open()
        return snackbar
