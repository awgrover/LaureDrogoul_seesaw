#!/usr/bin/env python

import pygst
pygst.require("0.10")
import gst
import pygtk, gtk

def __get_pad_callback(dbin, pad, is_last):
    print "  callback link %s -> %s" % (dbin, dbin.__want)
    pad.link(dbin.__want.get_pad('sink'))

def append_pipe(pipe, name, element_name, properties):
    element = gst.element_factory_make(element_name, name)
    for k,v in properties.iteritems():
        element.set_property(k,v)
    pipe.add(element)
    if hasattr(pipe, '__previous'):
        print "from %s -> %s" % (pipe.__previous.__class__.__name__, element.__class__)
        print "Link %s -> %s" % (pipe.__previous,element)
        # can't use instanceof() because the classes may not be loaded
        if pipe.__previous.__class__.__name__ == '__main__.GstDecodeBin' or pipe.__previous.__class__.__name__ == '__main__.GstDecodeBin2':
            print "  dbin special link"
            pipe.__previous.__want = element
            pipe.__previous.connect("new-decoded-pad", __get_pad_callback)
        else:
            pipe.__previous.link(element)
    else:
        print "first for pipe %s : %s" % (pipe,element)
    pipe.__previous = element
    return element

def main():
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
