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
        # print "from %s -> %s" % (pipe.__previous.__class__, element.__class__)
        print "Link %s -> %s" % (pipe.__previous,element)
        if isinstance(pipe.__previous, GstDecodeBin):
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
    pipe = gst.Pipeline("test")

    # fromfile = gst.element_factory_make('audiotestsrc','testfile')
    # fromfile = gst.element_factory_make('filesrc','testfile')
    # fromfile.set_property('location','falling.wav')
    # fromfile.set_state(gst.STATE_PLAYING)
    # gtk.main()
    append_pipe(pipe, 'testfile', 'filesrc', { 'location' : 'falling.wav' })
    append_pipe(pipe, 'decodebin2', 'decodebin', {})
    append_pipe(pipe, 'audioconvert', 'audioconvert', {})
    append_pipe(pipe, 'alsasink', 'alsasink', {})
    
    pipe.set_state(gst.STATE_PLAYING)

    gtk.main()

main()
