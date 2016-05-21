# internal invocations:
# env PI=1|2 SDROOTFS=/mnt/$thesdrootfs
source_dirs :=etc root home
sources := $(shell find $(source_dirs) -type f )
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
	@echo "---"; echo "DO THIS:"
	@echo "scp rp$(PI).tar raspberrypi$(PI).local:"
	@echo "ssh raspberrypi$(PI).local"; echo "sudo su"; echo "cd"; echo "(cd / && tar xf ~pi/rp$(PI).tar)"
	@echo "apt-get update"
	@echo "make setup"

.PHONY : copy_to_sd
copy_to_sd : check $(sources) edit tarify
	@if [ "$$SDROOTFS" == '' ]; then echo "Expected SDROOTFS"; exit 1; fi
	cd $$SDROOTFS && tar xf $(CURDIR)/rp$(PI).tar
	chmod 774 $$SDROOTFS/etc/config_once.conf
	chown 0.0 $$SDROOTFS/etc/config_once.conf

.PHONY : check
check :
	@if [ "$$PI" == '' ]; then echo "target is internal"; exit 1; fi
	echo Make: $$PI

.PHONY : tarify
tarify : $(source_dirs) Makefile
	tar cf rp$(PI).tar $(source_dirs)

# Especially after copy_to_sd (: edit)
.PHONE : clean
clean : 
	git checkout HEAD etc/network/interfaces.d
	cd ..; git status --porcelain install/etc/network/interfaces.d | grep '?' | awk '{print $$2}' | xargs --no-run-if-empty rm
	cd home/pi/fun; rm -f 2*.wav seesawsound2.wav 1*.wav seesawsound.wav 2>/dev/null || true

.PHONY : edit
edit :  $(sources) Makefile
	cp -pr ../pi_fun home/pi/fun
	cd home/pi/fun; rm 2*.wav seesawsound2.wav 1*.wav seesawsound.wav 2>/dev/null || true
	cp ../currentfiles/2* ../currentfiles/1* home/pi/fun
	cd home/pi/fun; ln -s 2*.wav seesawsound2.wav; ln -s 1*.wav seesawsound.wav
	sed -i -e '/ wireless-essid / s/Pi./Pi$(PI)/' -e '/ address / s/[^.]\+$$/$(PI)/' etc/network/interfaces.d/adhocpi
	if [ "$$WIFI" != '' ]; then mv etc/network/interfaces.d/$$WIFI etc/network/interfaces.d/$$WIFI.conf; fi
	echo raspberrypi$$PI > etc/hostname
