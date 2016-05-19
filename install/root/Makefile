rcdirs := $(shell /bin/ls -d /etc/rc?.d | grep -v rcS.d)
tarpayload := $(shell tar tf rp?.tar | sort -u)
packages_needed := $(shell dpkg-query --show -f '${db:Status-Abbrev} ${Package}\n' isc-dhcp-server tightvncserver | egrep '^un' | awk '{print $2}')

.PHONY : setup
setup : /etc/shadow /etc/network/interfaces /etc/dhcp/dhcpd.conf wifi packages /home/pi/.vnc/passwd $(rcdirs) 
	@echo "cd /etc/network/interfaces.d" echo "./pick *something*"


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

.PHONE : wifi
wifi :
	service networking restart	
	bash -c "while ! ip route list | grep 'default via'; do sleep 1; if (( SECONDS > 60 )); then exit 1; fi; done"

.PHONY : packages
packages :
	apt-get update
	if [ "$(packages_needed)" != '' ]; then apt-get install $(packages_needed); fi
