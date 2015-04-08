#!/usr/bin/env python

import sys
import swmixer
import numpy

import pyaudio
import pprint

pprint.pprint( pyaudio.PyAudio().get_host_api_info_by_index(0))

exit(1)
swmixer.init(samplerate=44100, chunksize=1024, stereo=False, microphone=True)
snd = swmixer.Sound("falling.wav")
snd.play(loops=-1)

micdata = []
frame = 0

while True:
    swmixer.tick()
    if False:
        frame += 1
        micdata = numpy.append(micdata, swmixer.get_microphone())
        if True or frame > 1:
            micsnd = swmixer.Sound(data=micdata)
            micsnd.play()
            micdata = []
            frame = 0
