# Makes tars ('all') than can be untarred onto a rootfs to configure it ('config_sd')
# Uses the sound files ../currentfiles/2*,1*
# env WIFI=once_wificonfigname rp$n.tar # clean if you change WIFI
# sudo env SDROOTFS=/mnt/somesdrootfs config_sd$n # to edit the rootfs with the config for pi$n

# internal invocations:
# env PI=1|2 SDROOTFS=/mnt/$thesdrootfs

source_dirs_root :=etc root
source_dirs :=$(source_dirs_root) home
sources := $(shell find $(source_dirs) -type f )
SHELL := /bin/bash

all : rp1.tar rp2.tar rp3.tar

# rp%.tar : $(sources) Makefile
.PRECIOUS : rp%.tar
rp%.tar : build/rp% Makefile
	tar cf rp$*.tar -C $< .

# Copy the source_dirs and edit them
# (might not use actual currentfiles/ if the source_dirs have a newer!)
.PRECIOUS : build/rp%
build/rp% : $(sources) ../currentfiles/2* ../currentfiles/1* Makefile
	# clean $@
	if [ -e $@ ]; then rm -rf $@; fi
	mkdir -p $@
	cp -pr $(source_dirs) $@
	# make edits for the sound files
	cd $@/home/pi/fun; rm 2*.wav seesawsound2.wav 1*.wav seesawsound.wav 2>/dev/null || true
	cp ../currentfiles/2* ../currentfiles/1* $@/home/pi/fun
	cd $@/home/pi/fun; ln -s 2*.wav seesawsound2.wav; ln -s 1*.wav seesawsound.wav
	# make edits for the wifi
	sed -i -e '/ wireless-essid / s/Pi./Pi$*/' -e '/ address / s/[^.]\+$$/$*/' $@/etc/network/interfaces.d/adhocpi
	if [ "$$WIFI" != '' ]; then \
		mv $@/etc/network/interfaces.d/$$WIFI $@/etc/network/interfaces.d/$$WIFI.conf; \
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
.PHONY : obs1
obs1 : $(sources) Makefile 
	# this used to be the manual way to use tar
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

# Expects this to be run as SU
.PHONY : config_sd%
config_sd% : $(SDROOTFS) rp%.tar
	@if [ "$$SDROOTFS" == '' ]; then echo "Expected env SDROOTFS=/some-sdrootfs"; exit 1; fi
	@if [ ! -e rp$*.tar ]; then echo "make the rp$*.tar first (see comments in Makefile)"; exit 1; fi
	@if [ ! -e $$SDROOTFS/etc/passwd ]; then echo "Expected at least /etc/passwd on $$SDROOTFS"; exit 1; fi
	cd $$SDROOTFS && tar xf $(CURDIR)/rp$*.tar
	# Fix ownership
	for f in `find $(source_dirs_root)`; do \
		chown 0.0 $$SDROOTFS/$f; \
	done
	rpuser=`egrep '^pi: $$SDROOTFS/etc/passwd | awk -F: '{print $1,$3}'`; \
	for f in `find home/pi`; do \
		chown -R $rpuser.$rpuser $f; \
	done
	chmod 774 $$SDROOTFS/etc/config_once.conf
	find $$SDROOTFS/etc/avahi -type d | xargs chmod 755
	find $$SDROOTFS/etc/avahi -type f | xargs chmod 644

.PHONY : clean
clean : 
	rm -rf build
	@echo "You must 'rm' the tar of interest"

