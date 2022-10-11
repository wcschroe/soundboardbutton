import vlc, os, time
from threading import Thread
from mutagen.mp3 import MP3
import RPi.GPIO as GPIO
from random import shuffle
from queue import Queue

class SoundBoardButton():
    def __init__(self, GPIO_Pin:int):
        # create audio player
        self.player:vlc.MediaPlayer = vlc.MediaPlayer()
        # create lists and queues
        self.soundqueue = Queue()
        self.soundlist = []
        # store pin value
        self.GPIO_Pin = GPIO_Pin
        # setup pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_Pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.GPIO_Pin, GPIO.RISING, callback=self.play_callback, bouncetime=2000)
        # enqueue sounds
        self.fill_queue()

    def fill_queue(self):
        self.soundlist = []
        ready_sound:str = ''
        working_dir:str = os.path.dirname(__file__)
        # look for mp3 files
        for path, subdirs, files in os.walk(working_dir):
            for name in files:
                filePath:str = os.path.join(path, name)
                if '.mp3' in filePath:
                    if 'oou' in filePath: # set ready sound if found
                        ready_sound = filePath
                    self.soundlist.append(filePath)

        shuffle(self.soundlist) # shuffle sounds
        for sound in self.soundlist:
            self.soundqueue.put(sound) # enqueue sounds
        print(self.soundlist)

        # play sound so we know the soundboard is ready
        self.play_sound(ready_sound)
        self.play_sound(ready_sound)

    def play_sound(self, sound:str):
        print(f'playing {sound}')

        # setup sound
        sound_length = MP3(sound).info.length
        self.player = vlc.MediaPlayer(sound)
        self.player.audio_set_volume(100)

        # play sound
        self.player.play()

        # wait for sound to finish
        time.sleep(sound_length + .5)

        # stop when done
        self.player.stop()

    def play_callback(self, channel:int):
        # temporarily disable button presses
        GPIO.remove_event_detect(channel)

        # fill queue if empty
        if self.soundqueue.empty():
            self.fill_queue()

        # get sound and play
        try:
            sound:str = self.soundqueue.get_nowait()
            self.play_sound(sound)
        except:
            pass
        
        # re-enable button presses
        GPIO.add_event_detect(channel, GPIO.RISING, callback=self.play_callback, bouncetime=2000)

if __name__ == '__main__':
    # init object with pin 17 (button)
    sb = SoundBoardButton(17)

    # sleep loop forever, so button events can happen asynchronously
    while True:
        time.sleep(1)


