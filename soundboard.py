import vlc, os, time
from threading import Thread
from mutagen.mp3 import MP3
import RPi.GPIO as GPIO
from random import shuffle
from queue import Queue

class SoundBoardButton():
    def __init__(self, GPIO_Pin:int):
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
                    else:
                        self.soundlist.append(filePath)

        shuffle(self.soundlist) # shuffle sounds
        for sound in self.soundlist:
            self.soundqueue.put(sound) # enqueue sounds

        # play sound so we know the soundboard is ready
        self.play_sound(ready_sound)
        self.play_sound(ready_sound)

    def play_sound(self, sound:str):
        print(f'playing {sound}')

        # get sound length
        sound_length = MP3(sound).info.length

        # setup sound
        play_start = time.time()
        self.p:vlc.MediaPlayer = vlc.MediaPlayer(sound)

        # play sound
        self.p.play()
        play_finish = time.time()

        # wait for sound to finish and stop
        time.sleep(sound_length + (play_finish - play_start))
        self.p.stop()


    def play_callback(self, channel:int):
        # temporarily disable button presses
        GPIO.remove_event_detect(channel)

        # fill queue if empty
        if self.soundqueue.empty():
            self.fill_queue()

        # get sound and play
        sound:str = self.soundqueue.get()
        self.play_sound(sound)
        
        # re-enable button presses
        GPIO.add_event_detect(channel, GPIO.RISING, callback=self.play_callback, bouncetime=2000)

if __name__ == '__main__':
    # init object with pin 17 (button)
    sb = SoundBoardButton(17)

    # sleep loop forever, so button events can happen asynchronously
    while True:
        time.sleep(1)


