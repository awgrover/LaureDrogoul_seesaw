# Makes tars ('all') than can be untarred onto a rootfs to configure it ('copy_to_sd')
# Uses the sound files ../currentfiles/2*,1*
# env WIFI=once_wificonfigname SDROOTFS=/mnt/somesdrootfs --- 

# internal invocations:
# env PI=1|2 SDROOTFS=/mnt/$thesdrootfs

source_dirs :=etc root home
sources := $(shell find $(source_dirs) -type f )
SHELL := /bin/bash

all : rp1.tar rp2.tar rp3.tar

# rp%.tar : $(sources) Makefile
rp%.tar : build/rp% Makefile
	tar cf rp$*.tar -C $< .

# Copy the source_dirs and edit them
# (might not use actual currentfiles/ if the source_dirs have a newer!)
build/rp% : $(sources) ../currentfiles/2* ../currentfiles/1* Makefile
	# clean $@
	if [ -e $@ ]; then rm -rf $@; fi
	mkdir -p $@
	cp -pr $(source_dirs) $@
	# make edits for the pi# (wifi), and the sound files
	# make edits for the sound files
	cd $@/home/pi/fun; rm 2*.wav seesawsound2.wav 1*.wav seesawsound.wav 2>/dev/null || true
	cp ../currentfiles/2* ../currentfiles/1* $@/home/pi/fun
	cd $@/home/pi/fun; ln -s 2*.wav seesawsound2.wav; ln -s 1*.wav seesawsound.wav
	# make edits for the wifi
	sed -i -e '/ wireless-essid / s/Pi./Pi$*/' -e '/ address / s/[^.]\+$$/$*/' $@/etc/network/interfaces.d/adhocpi
	if [ "$$WIFI" != '' ]; then \
		mv etc/network/interfaces.d/$$WIFI etc/network/interfaces.d/$$WIFI.conf; \
	else \
		echo "### Did not setup the wifi-once-on-boot network, use env WIFI=xxx to do so"; \
	fi
	echo raspberrypi$* > $@/etc/hostname

	@# make sure the build dir has the correct make-time
	touch $@

.PHONY : from
from :
	@echo $(sources) | xargs ls -l

# Assume the rest is for the "recusive" make:

# OBS
.PHONY : editntarify
editntarify : check $(sources) Makefile edit tarify
	@echo "---"; echo "DO THIS:"
	@echo "scp rp$(PI).tar raspberrypi$(PI).local:"
	@echo "ssh raspberrypi$(PI).local"; echo "sudo su"; echo "cd"; echo "(cd / && tar xf ~pi/rp$(PI).tar)"
	@echo "apt-get update"
	@echo "make setup"


# Untar onto a rootfs, so it should be ready to boot
# assumes a rootfs at $SDROOTFS, untars onto it, and does some other config
.PHONY : config_sd
config_sd :
	@echo "Need a pi # for config_sdn"

.PHONY : config_sd%
config_sd% : $(SDROOTFS) rp%.tar
	@if [ "$$SDROOTFS" == '' ]; then echo "Expected env SDROOTFS=/some-sdrootfs"; exit 1; fi
	echo "ok: $*" 

# OBS
.PHONY : copy_to_sd
copy_to_sd : check $(sources) edit tarify
	@if [ "$$SDROOTFS" == '' ]; then echo "Expected SDROOTFS"; exit 1; fi
	cd $$SDROOTFS && tar xf $(CURDIR)/rp$(PI).tar
	chmod 774 $$SDROOTFS/etc/config_once.conf
	chown 0.0 $$SDROOTFS/etc/config_once.conf
	chown -R 0.0 $$SDROOTFS/etc/avahi
	find $$SDROOTFS/etc/avahi -type d | xargs chmod 755
	find $$SDROOTFS/etc/avahi -type f | xargs chmod 644

# OBS
.PHONY : check
check :
	@if [ "$$PI" == '' ]; then echo "target is internal"; exit 1; fi
	echo Make: $$PI

# OBS
.PHONY : tarify
tarify : $(source_dirs) Makefile
	tar cf rp$(PI).tar $(source_dirs)

.PHONE : clean
clean : 
	rm -rf build

# OBS
# Sadly, I'm editing the sources, I should make a copy in a "build/"
.PHONY : edit
edit :  $(sources) Makefile
	if [ -e home/pi/fun ]; then rm -rf home/pi/fun; fi; cp -pr ../pi_fun home/pi/fun
	# make edits for the pi# (wifi), and the sound files
	cd home/pi/fun; rm 2*.wav seesawsound2.wav 1*.wav seesawsound.wav 2>/dev/null || true
	cp ../currentfiles/2* ../currentfiles/1* home/pi/fun
	cd home/pi/fun; ln -s 2*.wav seesawsound2.wav; ln -s 1*.wav seesawsound.wav
	sed -i -e '/ wireless-essid / s/Pi./Pi$(PI)/' -e '/ address / s/[^.]\+$$/$(PI)/' etc/network/interfaces.d/adhocpi
	if [ "$$WIFI" != '' ]; then mv etc/network/interfaces.d/$$WIFI etc/network/interfaces.d/$$WIFI.conf; fi
	echo raspberrypi$$PI > etc/hostname
