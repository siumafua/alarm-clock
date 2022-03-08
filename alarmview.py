class AlarmView(ModalView):
    
    alarm_audio = ObjectProperty()
    pause = BooleanProperty(False)
    nloop = NumericProperty(0)

    def __init__(self, **kwargs):
        
        # process then remove our own arguments
        # before calling super otherwise it will raise an error
        # since parent class will not recognizes it.
        
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
        
        # let the open process complete then 
        # start the alarm    
        self.start_alarm()

    def start_alarm(self):
        
        self.ids.pause.disabled = False
        self.ids.resume.disabled = True
        self.alarm_audio = SoundLoader.load(self.audio)

        # we take care of looping so turn this off.
        # we need to control the number of loops etc
        self.alarm_audio.loop = False
        
        # just to be sure as state don't change when the sound
        # reach the end...
        if self.alarm_audio.state != 'stop':
            self.alarm_audio.stop()
            
        # number of loops = duration in secs / length of audio in secs
        # duration = 5 mins = 300 secs and audio length = 20 secs  
        # self.nloop = 300 / 20 = 15 
        
        self.nloop = self.dura * 60 / self.alarm_audio.length
        
        # setup callback for when the alarm audio reach the end
        # we need to restart "nloop" times. 
        
        self.alarm_audio.bind(on_stop=self.stopping)
        
        # play the alarm sound
        self.alarm_audio.play()

    def set_volume(self, val):
        self.alarm_audio.volume = val

   
    def stopping(self, obj):
        """stopping - Called when alarm stop playing.

        Keep replaying the alarm audio unless the user
        paused it (clicking pause) or we reach the number 
        of loops i.e. have played the audio for "duration" secs 
            
        Args:
            obj : ignored
        """
    
        if not self.pause and self.nloop > 0:
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
