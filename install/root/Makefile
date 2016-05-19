rcdirs := $(shell /bin/ls -d /etc/rc?.d | grep -v rcS.d)
tarpayload := $(shell tar tf rp?.tar | sort -u)
packages_needed := $(shell dpkg-query --show -f '${db:Status-Abbrev} ${Package}\n' isc-dhcp-server tightvncserver python-smbus i2c-tools gstreamer1.0-tools gstreamer0.10-alsa python-gst0.10 python-gtk2 gstreamer0.10-plugins-good:armhf avahi-daemon libnss-mdns xrdp | egrep '^un' | awk '{print $2}')

.PHONY : setup
setup : /home/pi/.ssh /etc/shadow /etc/hosts /etc/network/interfaces /etc/dhcp/dhcpd.conf wifi /etc/ssh/sshd_config packages /home/pi/.vnc/passwd $(rcdirs) /etc/modprobe.d/alsa-base.conf /etc/rc.local /etc/logrotate.d/rsyslog /etc/modules /boot/config.txt
	@echo "cd /etc/network/interfaces.d" echo "./pick *something*"
	@echo "Wants to reboot (if alsa-base was edited"
	@echo "Wants to reboot to start everything up"


/etc/hosts : Makefile
	hname=`hostname` sed -i -e '/raspberrypi/ d' -e "a 127.0.1.1 $$hname" /etc/hosts

/home/pi : Makefile
	adduser --home /home/pi --no-create-home pi

.PHONY : /home/pi/.ssh
/home/pi/.ssh : /home/pi Makefile
	chown pi.pi $@
	chmod -R 660 $@
	chmod 770 $@

/boot/config.txt : Makefile
	sed -i 'a dtparam=i2c1=on' /boot/config.txt

/etc/modules : Makefile
	sed -i -e 'a i2c-bcm2708' -e 'a i2c-dev' /etc/modules

/etc/logrotate.d/rsyslog : Makefile
	sed -i '/daily/ i size 1M' /etc/logrotate.d/rsyslog

/etc/rc.local : Makefile
	sed -i '/exit 0/ i (cd ~pi/fun && ./driver.py |& logger -t seesaw)&' /etc/rc.local

/home/pi/.vnc/passwd : Makefile
	mkdir -p `dirname $@`
	echo BitbCLx7 | su pi vncpasswd -f > $@
	chown -R pi.pi `dirname $@`
	chmod 600 $@

/etc/shadow : Makefile
	(echo BitbCLx7; echo BitbCLx7) | passwd pi

$(rcdirs): /etc/init.d/tightvnc
	ps -C Xtightvnc && service tightvnc stop
	chmod ug+x /etc/init.d/tightvnc
	update-rc.d tightvnc defaults
	service tightvnc start

/etc/network/interfaces : Makefile
	sed -i.bak '/wlan0/ d' $@
	egrep '^source' $@ 2>/dev/null || echo 'source /etc/network/interfaces.d/*.conf' >> $@

/etc/dhcp/dhcpd.conf : edits/dhcpd.conf Makefile
	sed -i.bak '/^subnet 192\.168\.99\.0 /,99 d' $@
	cat $< >> $@

/etc/modprobe.d/alsa-base.conf : Makefile
	sed -i.was '/snd-usb-audio/ s/-2/0/' /etc/modprobe.d/alsa-base.conf

/etc/ssh/sshd_config : Makefile
	echo "UseDNS no" >> /etc/ssh/sshd_config && service ssh restart

.PHONE : wifi
wifi :
	service networking restart	
	bash -c "while ! ip route list | grep 'default via'; do sleep 1; if (( SECONDS > 60 )); then exit 1; fi; done"

.PHONY : packages
packages :
	apt-get update
	if [ "$(packages_needed)" != '' ]; then apt-get install $(packages_needed); fi
	easy_install-pypy pygst
