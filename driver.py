#!/usr/bin/env python
# runs 2 'mixer.py', adjusting the volumes based on attitude w/self-calibration
# For the file, looks for seesawsound.wav, or argv[1]

import sys
import threading
from threading import Thread
import time
import os
from subprocess import Popen
import subprocess
from collections import deque
from random import randint
import RPi.GPIO as GPIO
import os


def debug(*x):
    msg = "[D] "
    for m in x:
        msg += str(m)
        msg += " "
    msg += "\n"
    sys.stderr.write(msg)

if os.environ.get('DEBUG') == '2':
    def debug2(*x):
        debug(2,*x)
else:
    def debug2(*x):
        pass

class Tilt(object):
    first_time = True

    def __init__(self, pin, name):
        debug("Setup tilt '%s' on %s" %(name,pin))
        self.name=name
        self.pin = pin
        self.ma = Simplemovingaverage(5)
        if Tilt.first_time:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            Tilt.first_time=False
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # open is pull-up, and "detect" is low
        self._went_on = False
        GPIO.add_event_detect(pin, GPIO.BOTH, callback=self.note_on, bouncetime=200)

    def note_on(self, pin):
        if GPIO.input(pin):
            if not self._went_on:
                debug2("Went on %s" % pin)
            self._went_on = True
        else:
            debug2("Went off %s" % pin)
            self._went_on = False

    def readpin(self):
        if randint(1,10) == 1:
            return True
        else:
            return False

    def went_on(self):
        # one-shot
        if self._went_on:
            self._went_on = False
            return True
        else:
            return False

    def __add__(self,operand):
        # tracks another value for calibrating to absolute
        self.ma(operand)
        return self

    def average(self):
        return self.ma.average

class Simplemovingaverage():
    # from http://rosettacode.org/wiki/Averages/Simple_moving_average#Python

    def __init__(self, period):
        assert period == int(period) and period > 0, "Period must be an integer >0"
        self.period = period
        self.stream = deque()
        self.average = 0
 
    def __call__(self, n):
        stream = self.stream
        stream.append(n)    # appends on the right
        streamlength = len(stream)
        if streamlength > self.period:
            stream.popleft()
            streamlength -= 1
        if streamlength == 0:
            self.average = 0
        else:
            self.average = sum( stream ) / streamlength
 
        return self.average
    
from smbus import SMBus
from my_LSM9DS0 import LSM9DS0

class Attitude(Thread):
    start_val = 'b' # b is the sound file
    current = start_val
    current_raw = 1000
    
    # so we can get to them:
    tilta = Tilt(14, 'a') # means, on when 'a' is down
    tiltb = Tilt(15, 'b')
    tilt_point = 1000
    lsm = LSM9DS0(SMBus(1))

    def run(self):
        debug("Start tracking attitude")
        self.ma = Simplemovingaverage(10)
        Thread(None,self.lsm.update).start()
        while(True):
            self.using_gyro()
            # self.using_tilt()
            time.sleep(0.01)

    def using_tilt(self):
        if self.tiltb.went_on():
            debug2("play is %s" % self.tiltb.name)
            Attitude.current = self.tiltb.name
        elif self.tilta.went_on():
            debug2("play is %s" % self.tilta.name)
            Attitude.current = self.tilta.name

    def using_gyro(self):
        self.__class__.current_raw = self.ma(self.readval())
        change = self.current_raw - self.tilt_point
        debug2("gyro @ %s delta %s" % (self.current_raw, change))
        if change < 0:
            if self.current != 'b':
                debug2("TO B %s vs %s +- %s" % (self.current_raw, self.tilt_point, change))
                self.__class__.current = 'b'
        elif change > 0:
            if self.current != 'a':
                debug2("TO A %s vs %s +- %s" % (self.current_raw, self.tilt_point, change))
                self.__class__.current = 'a'

    def readval(self):
       return int(self.lsm.accel[0])/10 # x, lsd is noisy

class AMixer(Thread):
    my_vol = 100

    def launch_mixer(self,index, cli2=None):
        self.index = index
        debug("Launch: mixer.py %s '%s'" % (self.index, cli2))
        self.mixer_in = Popen(['python', './mixer.py', str(index), cli2 or ''], stdin=subprocess.PIPE).stdin

    def set_volume(self, to, taking):
        debug2("volume of %s [mixin %s] -> %s in %smsec" % (self.index, self.mixer_in, to, taking))
        self.mixer_in.write("%s %s\n" % (to, taking))

    def run(self):
        debug("Start thread for %s" % self.__class__)
        self.launch_mixer(self.my_index)
        was = None
        while(True):
            if was != Attitude.current:
                if Attitude.current == self.my_side:
                    debug2( "On idx %s: %s -> %s" % (self.index, was,Attitude.current))
                    self.set_volume(self.my_vol,100)
                else:
                    debug2( "Off idx %s: %s -> %s" % (self.index, was,Attitude.current))
                    self.set_volume(0,100)
                was = Attitude.current
            time.sleep(0.05)

class RunMic(AMixer):
    my_index = 1
    my_side = 'a'
    my_vol = 200

class RunFile(AMixer):
    my_index = 2
    my_side = 'b'

    def launch_mixer(self, index):
        debug("Launch %s mixer" % self.__class__)
        super(self.__class__, self).launch_mixer(index, self.find_file())

    def find_file(self):
        if len(sys.argv) > 1 and sys.argv[1]:
            return sys.argv[1]
        elif os.path.isfile("seesawsound.wav"):
            return "seesawsound.wav"
        else:
            sys.stderr.write("No sound: no extant seesawsound.wav, no argv[1]\n")
            return None

class RunFile_A(AMixer):
    my_index = 2
    my_side = 'a'

    def launch_mixer(self, index):
        debug("Launch %s mixer" % self.__class__)
        super(self.__class__, self).launch_mixer(index, self.find_file())

    def find_file(self):
        if os.path.isfile("seesawsound2.wav"):
            return "seesawsound2.wav"
        else:
            sys.stderr.write("No sound: no extant seesawsound2.wav, no argv[1]\n")
            return None

def debug_thread_ct():
    # log thread ct
    was = 0
    while (True):
        isnow = threading.active_count()
        if isnow != was:
            debug("Threads:",isnow)
            was=isnow
        time.sleep(5)

def start_debug():
    Thread(None, debug_thread_ct, 'debug_thread_ct').start()
    debug("Starting start_debug")

def start_self_calibration():
    debug("Begin self-calibration")
    while(True):
        for atilt in (Attitude.tilta, Attitude.tiltb):
            if atilt.went_on():
                atilt += Attitude.current_raw # calcs average, used by attitude
                debug("Update %s: %s -> %s" % (atilt.name, Attitude.current_raw, atilt.average()))
                Attitude.tilt_point = (Attitude.tilta.average() + Attitude.tiltb.average()) /2
        time.sleep(.01)
        
def main():
    start_debug()

    # RunMic(name= 'mic').start() # starts off, monitors attitude
    RunFile_A(name='filea').start()
    RunFile(name='file').start() # starts on, monitors attitude

    Thread(None, start_self_calibration, 'self_calibration').start() # messes with horiz reference
    Attitude(name='attitude').start() # use ref, set attitude

main()
