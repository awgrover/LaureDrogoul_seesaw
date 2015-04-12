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

class Attitude(object):
    start_val = 'b'
    current = start_val


def debug(*x):
    msg = "[D] "
    for m in x:
        msg += str(m)
        msg += " "
    msg += "\n"
    sys.stderr.write(msg)

class AMixer(Thread):
    my_vol = 100

    def launch_mixer(self,index, cli2=None):
        self.index = index
        debug("Launch: mixer.py %s '%s'" % (self.index, cli2))
        self.mixer_in = Popen(['python', './mixer.py', str(index), cli2 or ''], stdin=subprocess.PIPE).stdin

    def set_volume(self, to, taking):
        debug("volume of %s -> %s in %smsec" % (self.index, to, taking))
        self.mixer_in.write("%s %s\n" % (to, taking))

    def run(self):
        debug("Start thread for %s" % self.__class__)
        self.launch_mixer(self.my_index)
        was = None
        while(True):
            if was != Attitude.current:
                debug( "Change %s: %s -> %s" % (self.index, was,Attitude.current))
                was = Attitude.current
                if was == self.my_side:
                    self.set_volume(my_vol,0)
                elif was == 'b':
                    self.set_volume(0,0)

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
        
def debug_thread_ct():
    while (True):
        debug("Threads:",threading.active_count())
        time.sleep(5)

def start_debug():
    Thread(None, debug_thread_ct, 'debug_thread_ct').start()
    debug("Starting start_debug")

def main():
    start_debug()

    debug("runners...")
    RunMic(name= 'mic').start() # starts off, monitors attitude
    RunFile(name='file').start() # starts on, monitors attitude
    debug("...runners")

    """
    start_self_calibration() # messes with horiz reference
    start_attitude() # use ref, set attitude
    """

main()
