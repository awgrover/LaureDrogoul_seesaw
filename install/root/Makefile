pipasswd :=BitbCLx7
rcdirs := $(shell /bin/ls -d /etc/rc?.d | grep -v rcS.d)
# tarpayload := $(shell tar tf rp?.tar | sort -u)
packages_needed := isc-dhcp-server tightvncserver python-smbus i2c-tools gstreamer1.0-tools gstreamer0.10-alsa python-gst0.10 python-gtk2 gstreamer0.10-plugins-good:armhf avahi-daemon libnss-mdns xrdp

.PHONY : setup
setup : /home/pi/.ssh /etc/shadow /etc/hosts /etc/network/interfaces  /etc/ssh/sshd_config packages /etc/init.d/tightvnc /etc/modprobe.d/alsa-base.conf /etc/rc.local /etc/logrotate.d/rsyslog /etc/modules /boot/config.txt
	@echo "cd /etc/network/interfaces.d" echo "./pick *something*"
	@echo "Wants to reboot (if alsa-base was edited"
	@echo "Wants to reboot to start everything up"


# All these "edits" are .phony because I don't have anything to depend-on
# So, always run them but make them idempotent

.PHONY : /etc/hosts
/etc/hosts :
	grep raspberrypi $@ || (hname=`hostname`; sed -i -e '/raspberrypi/ d' -e "$$ a 127.0.1.1 $$hname" /etc/hosts)

.PHONY : /home/pi
/home/pi :
	adduser --home /home/pi --no-create-home pi || true
	chown -R pi.pi /home/pi

.PHONY : /home/pi/.ssh
/home/pi/.ssh : /home/pi
	chown -R pi.pi $@
	chmod -R 660 $@
	chmod 770 $@

.PHONY : /boot/config.txt
/boot/config.txt :
	grep dtparam=i2c1=on $@ || sed -i '$$ a dtparam=i2c1=on' $@

.PHONY : /etc/modules
/etc/modules :
	grep i2c-bcm2708 $@ || sed -i -e '$$ a i2c-bcm2708' -e '$$ a i2c-dev' $@

.PHONY : /etc/logrotate.d/rsyslog
/etc/logrotate.d/rsyslog :
	grep 'size 1M' $@ || sed -i '/daily/ i size 1M' $@

.PHONY : /etc/rc.local 
/etc/rc.local : 
	grep driver.py $@ || sed -i '/exit 0/ i (cd ~pi/fun && ./driver.py |& logger -t seesaw)&' $@

.PHONY : /home/pi/.vnc/passwd
/home/pi/.vnc/passwd : /home/pi
	mkdir -p `dirname $@`
	chown -R pi.pi `dirname $@`
	@# replaces, so idempotent enough
	(echo $(pipasswd) | sudo -u pi vncpasswd -f > $@)
	chmod 600 $@

.PHONY : /etc/shadow 
/etc/shadow : 
	(echo $(pipasswd); echo $(pipasswd)) | passwd pi

.PHONY : rcdirs
rcdirs : 
	echo $(rcdirs)

.PHONY : /etc/init.d/tightvnc
/etc/init.d/tightvnc : /home/pi/.vnc/passwd
	ps -C Xtightvnc && service tightvnc stop || true
	chmod ug+x /etc/init.d/tightvnc
	update-rc.d tightvnc defaults
	service tightvnc start

.PHONY : /etc/network/interfaces
/etc/network/interfaces :
	grep wlan $@ && sed -i.bak '/wlan0/ d' $@ || true
	egrep '^source' $@ 2>/dev/null || echo 'source /etc/network/interfaces.d/*.conf' >> $@

# disabled, confuses eth0. after packages maybe
# not idempotent
# fix so that the "edits" are for wlan0, and eth0 just works
/etc/dhcp/dhcpd.conf : edits/dhcpd.conf
	touch $@
	sed -i.bak '/^subnet 192\.168\.99\.0 /,99 d' $@
	cat $< >> $@

.PHONY : /etc/modprobe.d/alsa-base.conf
/etc/modprobe.d/alsa-base.conf :
	@# is idempotent
	sed -i.was '/snd-usb-audio/ s/-2/0/' $@

.PHONY : /etc/ssh/sshd_config
/etc/ssh/sshd_config :
	grep 'UseDNS no' $@ || (echo "UseDNS no" >> $@ && service ssh restart)

# Disabled till wifi/dhcp/avahi figured out again
# after packages...
.PHONY : wifi
wifi :
	service networking restart
	bash -c "while ! ip route list | grep 'default via'; do sleep 1; if (( SECONDS > 60 )); then exit 1; fi; done"

.PHONY : packages
packages :
	apt-get update
	if [ "$(packages_needed)" != '' ]; then apt-get install $(packages_needed); fi
