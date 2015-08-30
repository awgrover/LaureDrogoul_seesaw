#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import threading

class Base(object):
    def setup(self):
        return self
    def run(self):
        pass


from smbus import SMBus
class Scan(Base):
    def __init__(self):
        self.found = []

    def setup(self):
        self.bus = SMBus(1)
        return self

    def run(self):
        for i in range(1,127):
            # rez = self.bus.read_byte(i)
            try:
                rez = self.bus.write_quick(i)
                self.found.append(i)
                print "%s -> %s" % (i,rez) 
            except IOError:
                pass
    def command(self,line):
        if re.search('^rescan$', line):
            self.run()
            if len(self.found) > 0:
                self.commander.default_address = self.found[0]
            return True
        elif re.search('^list$', line):
            for a in self.found:
                print a
            return True

    def help(self):
        return "rescan # rescan for i2c"


#define LSM9DS0_ADDRESS_ACCELMAG           (0x1D)         // 3B >> 1 = 7bit default
#define LSM9DS0_ADDRESS_GYRO               (0x6B)         // D6 >> 1 = 7bit default

import sys

class Commander(object):
    handlers = [] # classes
    commander = None

    def __init__(self, **kw):
        self.__class__.commander = self
        self.default_address = None
        self.handlers = []
        self.extra = kw
            
        for hc in self.__class__.handlers:
            print "make %s w/comm %s" % (hc,self)
            self.handlers.append( hc(self) )

    class CommandBase(object):
        # Subclasses should do this:
        @classmethod
        def register(self, someclass):
            Commander.handlers.append( someclass )

        def __init__(self, commander):
            print "made %s w/ com %s" % (self, commander)
            if not commander:
                raise Exception("no comm")
            self.commander=commander

        def command(self, line):
            raise Exception("what")


    def run(self):
        while(True):
            line = self.prompt()
            didit = False
            for handler in self.handlers:
                if handler.command(line):
                    didit = True
                    break
            if not didit:
                sys.stderr.write("Unrecognized: %s" % line)

    def prompt(self):
        if self.default_address:
            sys.stdout.write("@%s" % self.default_address)
        sys.stdout.write("> ")
        sys.stdout.flush()
        return sys.stdin.readline()

import re
class CommandHelp(Commander.CommandBase):
    def command(self, line):
        if re.search('^help$',line):
            for h in self.commander.handlers:
                print h.help()
            return True

    def help(self):
        return "help # print this"
Commander.CommandBase.register(CommandHelp)

class CommandI2C(Commander.CommandBase):
    def command(self,line):
        rez = re.search('(?:@(\d+)(?:\s+)?)?(?:(\d+)(?:=(\d+))?)?',line)
        if rez and rez.groups():
            print "groups %s" % str(rez.groups())
            addr,register,data = rez.groups()
            if register and data:
                if not addr:
                    addr = self.commander.default_address 
                print "write %s %s = %s" % (addr,register,data)
            elif register:
                if not addr:
                    addr = self.commander.default_address 
                print "read %s %s" % (addr,register)
                rez = self.commander.extra['i2c'].read_byte_data(int(addr), int(register))
                print  rez,"0x%02X" % rez
            elif addr:
                self.commander.default_address = addr
            else:
                return False
            return True
        
    def help(self):
        return "\n".join([
            "@$addr # default address for i2c commands",
            "[@$addr] $reg # read one byte from register",
            "[@$addr] $reg = $byte # write one byte to register"
            ])
Commander.CommandBase.register(CommandI2C)

from my_LSM9DS0 import LSM9DS0

class CommandLSM(Commander.CommandBase):
    def __init__(self, *args):
        super(CommandLSM, self).__init__(*args)
        self.lsm = LSM9DS0(self.commander.extra['i2c'])

    def help(self):
        return "accel # monitor accel/compass"

    def command(self,line):
        rez = re.search('accel',line)
        threading.Thread(None,self.lsm.update).start()
        if rez:
            print "accel .... compass"
            while(True):
                print self.lsm.accel,self.lsm.compass
                
        return False

Commander.CommandBase.register(CommandLSM)

def main():
    s = Scan()
    s.setup().run()

    c = Commander(i2c = s.bus)
    s.commander = c
    c.handlers.append(s)
    if len(s.found) > 0:
        c.default_address = s.found[0]
    c.run()

main()
