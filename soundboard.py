import vlc, os, time
from threading import Thread
from mutagen.mp3 import MP3
import RPi.GPIO as GPIO
from random import shuffle
from queue import Queue

class SoundBoardButton():
    def __init__(self, GPIO_Pin:int):
        self.soundqueue = Queue()
        self.soundlist = []
        self.GPIO_Pin = GPIO_Pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_Pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.GPIO_Pin, GPIO.RISING, callback=self.play_callback, bouncetime=2000)
        self.fill_queue()

    def fill_queue(self):
        self.soundlist = []
        ready_sound:str = ''
        for path, subdirs, files in os.walk('/home/william/GitHub/soundboard/'):
            for name in files:
                filePath:str = os.path.join(path, name)
                if '.mp3' in filePath:
                    if 'oou' in filePath:
                        ready_sound = filePath
                    else:
                        self.soundlist.append(filePath)

        shuffle(self.soundlist)
        for sound in self.soundlist:
            self.soundqueue.put_nowait(sound)
        self.play_sound(ready_sound)
        self.play_sound(ready_sound)

    def play_sound(self, sound:str):
        sound_length = MP3(sound).info.length
        play_start = time.time()
        self.p:vlc.MediaPlayer = vlc.MediaPlayer(sound)
        self.p.play()
        play_finish = time.time()
        time.sleep(sound_length + (play_finish - play_start))
        self.p.stop()


    def play_callback(self, channel:int):
        GPIO.remove_event_detect(channel)
        if self.soundqueue.empty():
            self.fill_queue()
        try:
            sound:str = self.soundqueue.get_nowait()
            self.play_sound(sound)
        except Exception as e:
            pass
        GPIO.add_event_detect(channel, GPIO.RISING, callback=self.play_callback, bouncetime=2000)

if __name__ == '__main__':
    sb = SoundBoardButton(17)
    while True:
        time.sleep(1)


