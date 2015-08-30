sources := $(shell find `find . -maxdepth 1 -type d | egrep -v '^\.$$'` -type f )
SHELL := /bin/bash

all : rp1.tar rp2.tar

%.tar : $(sources) Makefile
	@# just the 1 | 2:
	env PI=$(subst .tar,,$(subst rp,,$@)) make editntarify

.PHONY : from
from :
	@echo $(sources) | xargs ls -l

# Assume the rest is for the "recusive" make:

.PHONY : editntarify
editntarify : check $(sources) Makefile edit tarify
	@echo "---"; 
	@echo "scp rp$(PI).tar raspberrypi$(PI).local:"
	@echo "login"; echo "sudo su"; echo "cd"; echo "(cd / && tar xf ~pi/rp$(PI).tar)"
	@echo "make setup"

.PHONY : check
check :
	@if [ "$$PI" == '' ]; then echo "target is internal"; exit 1; fi
	echo Make: $$PI

tarify : $(sources) .edit
	tar cf rp`cat .edit`.tar $(sources)

edit :  $(sources) 
	sed -i '/wireless-essid/ s/Pi./Pi$(PI)/' etc/network/interfaces.d/adhocpi2.conf

