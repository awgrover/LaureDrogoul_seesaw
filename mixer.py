#!/usr/bin/env python

import pygst
pygst.require("0.10")
import gst
import pygtk, gtk

def __get_pad_callback(dbin, pad, is_last):
    # print "  callback link %s -> %s" % (dbin, dbin.__want)
    pad.link(dbin.__want.get_pad('sink'))

def append_pipe(pipe, name, element_name, properties):
    element = gst.element_factory_make(element_name, name)
    for k,v in properties.iteritems():
        element.set_property(k,v)
    pipe.add(element)
    if hasattr(pipe, '__previous'):
        # print "from %s -> %s" % (pipe.__previous.__class__.__name__, element.__class__)
        # print "Link %s -> %s" % (pipe.__previous,element)
        # can't use instanceof() because the classes may not be loaded
        if pipe.__previous.__class__.__name__ == '__main__.GstDecodeBin' or pipe.__previous.__class__.__name__ == '__main__.GstDecodeBin2':
            # print "  dbin special link"
            pipe.__previous.__want = element
            pipe.__previous.connect("new-decoded-pad", __get_pad_callback)
        else:
            pipe.__previous.link(element)
    else:
        # print "first for pipe %s : %s" % (pipe,element)
        pass
    pipe.__previous = element
    return element

import sys
import gobject
import re
from datetime import datetime,timedelta
vol = None
pipe = None
def main():
    global vol,pipe
    pipe = None
    if sys.argv[1] == '1':
        pipe,vol = do_mic()
    elif sys.argv[1] == '2':
        pipe,vol = do_file()
        print "pipe %s vol %s" % (pipe,vol)
    else:
        print "what?"
        exit(1)

    print "initial volume: %s" % vol.get_property('volume')
    gobject.io_add_watch(sys.stdin, gobject.IO_IN, adjust_volume)

    # gtk.main()

    if sys.argv[1] == '1':
        gtk.main()

    loop = gobject.MainLoop()
    gobject.threads_init()
    bus = pipe.get_bus()
    while(1):
        msg = bus.poll(gst.MESSAGE_ANY, -1)
        if msg.type != gst.MESSAGE_STATE_CHANGED:
            # print msg.type
            pass
        if msg.type == gst.MESSAGE_EOS:
           # print "--- EOS"
           # pipe,vol = do_file()
           pipe.set_state(gst.STATE_READY)
           pipe.set_state(gst.STATE_PLAYING)
        pass

fade = None # [ target %, by-msecs ]

def run_fade(setup):
    global vol,fade
    if not fade:
        return False

    delta_vol = int(fade[0]*100 - vol.get_property('volume') * 100)
    # print "f1 %s, dnow %s" % (fade[1], (fade[1] - datetime.now()).total_seconds())
    delta_msec = int((fade[1] - datetime.now()).total_seconds()*1000)
    # print "dv %s dm %s @ %s / %s" % (delta_vol, delta_msec, vol.get_property('volume'), datetime.now())
    if delta_msec <= 0:
        # print "past %s, so set to %s at %s" % (delta_msec,fade[0],datetime.now())
        vol.set_property('volume', fade[0])
        fade = None
    elif int(fade[0]*100) == int(vol.get_property('volume') * 100):
        # print "there"
        fade = None
    if not fade:
        # print "no more"
        return False

    step_vol = delta_vol / delta_msec
    if setup:
        step_msec = abs(delta_msec / delta_vol)
        if step_msec > 0:
            # print "Start w/msec interval %s" % step_msec
            gobject.timeout_add(step_msec, run_fade, None)
            # print "queued at %s" % datetime.now()
            return
        # print "start w/1 interval"
        gobject.timeout_add(1, run_fade, None)
        # print "queued at %s" % datetime.now()
        return

    if step_vol == 0:
        step_vol = +1
    # print '  adjust [%s] vol %s' % (sys.argv[1],step_vol)
    vol.set_property('volume', vol.get_property('volume') + step_vol/100.0)
    return True


def adjust_volume(io, why):
    # reads: target taking
    # target is a 0-100 percent (can overdrive!)
    # taking is msecs for the fade
    # why is the event

    global vol,fade
    input = sys.stdin.readline()
    input = input.rstrip()
    print "Adjust! [%s] g %s: %s" % (why, vol, input)
    is_fade = re.search('^([0-9]+)\s+([0-9]+)$', input)
    if is_fade:
        perc = int(is_fade.group(1))
        msecs = int(is_fade.group(2))
        # print "fade to %s%% in %s msecs" % (perc,msecs)
        # print "from %s" % datetime.now()
        fade = [ perc/100.0, datetime.now() + timedelta(milliseconds=msecs) ]
        # print "to %s by %s"  % ( fade[0], fade[1])
    if fade:
        run_fade(True)

    # print "volume: %s" % vol.get_property('volume')

    return True

def do_mic():
    ## Mic pipe
    micpipe = gst.Pipeline("micpipe")
    append_pipe(micpipe, 'mic', 'alsasrc',{})
    # append_pipe(micpipe, 'audioconvert', 'audioconvert', {})
    mic_volume = append_pipe(micpipe, 'micvolume', 'volume', {})
    append_pipe(micpipe, 'speaker', 'alsasink', {'sync' : False})
    micpipe.set_state(gst.STATE_PLAYING)
    return micpipe,mic_volume

def do_file_again(file_player):
    print "fired again"
    file_player.set_property('location', file_player.get_property('location'))

def note_signal(bus, message):
    global pipe
    # printing in here tends to cause seg fault
    # print "message! %s" % message
    # print "bob"
    if message.type == gst.MESSAGE_EOS:
        print "pipe %s" % pipe
        pipe.set_state(gst.STATE_NULL)
        pipe.set_state(gst.STATE_PLAYING)
    #    print message.structure.get_name()
    return gst.BUS_PASS

def do_file():
    filepipe = gst.Pipeline("filepipe")
    print "Play %s" % sys.argv[2]
    append_pipe(filepipe, 'testfile', 'filesrc', { 'location' : sys.argv[2] })
    # file_player.connect("about-to-finish", do_file_again)

    append_pipe(filepipe, 'decodebin', 'decodebin2', {})
    append_pipe(filepipe, 'audioconvert', 'audioconvert', {})
    file_volume = append_pipe(filepipe, 'filevolume', 'volume', {})
    append_pipe(filepipe, 'speaker', 'alsasink', {})

    # bus = filepipe.get_bus()
    # bus.add_signal_watch()
    # bus.enable_sync_message_emission()
    # bus.connect("message", note_signal)


    filepipe.set_state(gst.STATE_PLAYING)
    return filepipe,file_volume

def old():
    filepipe = gst.Pipeline("filepipe")

    # fromfile = gst.element_factory_make('audiotestsrc','testfile')
    # fromfile = gst.element_factory_make('filesrc','testfile')
    # fromfile.set_property('location','falling.wav')
    # fromfile.set_state(gst.STATE_PLAYING)
    # gtk.main()
    append_pipe(filepipe, 'testfile', 'filesrc', { 'location' : 'falling.wav' })
    append_pipe(filepipe, 'decodebin', 'decodebin2', {})
    append_pipe(filepipe, 'audioconvert', 'audioconvert', {})
    file_volume = append_pipe(filepipe, 'filevolume', 'volume', {})
    file_ident = gst.element_factory_make("identity")
    filepipe.add(file_ident) # needed?
    fileoutcaps = gst.caps_from_string("audio/x-raw-int,channels=2,rate=44100,depth=16")
    # isn't this just sequential 'link'?
    file_volume.link(file_ident, fileoutcaps)
    filepipe_srcpad = gst.GhostPad("src", file_ident.get_pad("src"))

    # append_pipe(filepipe, 'speaker', 'alsasink', {})
    # filepipe.set_state(gst.STATE_PLAYING)

    ## Mic pipe
    micpipe = gst.Pipeline("micpipe")
    append_pipe(micpipe, 'mic', 'alsasrc',{})
    mic_volume = append_pipe(micpipe, 'micvolume', 'volume', {})
    mic_ident = gst.element_factory_make("identity")
    micpipe.add(mic_ident) # needed?
    micoutcaps = gst.caps_from_string("audio/x-raw-int,channels=2,rate=44100,depth=16")
    # isn't this just sequential 'link'?
    mic_volume.link(mic_ident, micoutcaps)
    micpipe_srcpad = gst.GhostPad("src", mic_ident.get_pad("src"))

    # append_pipe(micpipe, 'speaker', 'alsasink', {})
    # micpipe.set_state(gst.STATE_PLAYING)

    # MIX
    mix = gst.Pipeline("mix")
    mix.add(filepipe)
    mix.add(micpipe)
    mixer = append_pipe(mix,"adder",'adder', {})

    ch1 = mixer.get_request_pad('sink%d')
    filepipe_srcpad.link(ch1)
    ch2 = mixer.get_request_pad('sink%d')
    micpipe_srcpad.link(ch2)

    append_pipe(mix, 'audioconvert', 'audioconvert', {})
    append_pipe(mix, 'mixspeaker', 'alsasink', {})

    mix.set_state(gst.STATE_PLAYING)



    gtk.main()

main()
