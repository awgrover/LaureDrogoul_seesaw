rcdirs := $(shell /bin/ls -d /etc/rc?.d | grep -v rcS.d)
edits := /etc/network/interfaces /etc/dhcp/dhcpd.conf /etc/shadow /etc/xrdp/startwm.sh
tarpayload := $(shell tar tf rp?.tar | sort -u)
packages_needed := dpkg-query --show -f '${db:Status-Abbrev} ${Package}\n' isc-dhcp-server tightvncserver xrdp | egrep '^un' | awk '{print $2}'

.PHONY : setup
setup : packages $(edits) $(rcdirs) /etc/shadow 
	@echo "cd /etc/network/interfaces.d" echo "./pick *something*"


/etc/shadow : Makefile
	(echo BitbCLx7; echo BitbCLx7) | passwd pi

$(rcdirs): /etc/init.d/tightvnc
	ps -C Xtightvnc && service tightvnc stop
	update-rc.d tightvnc defaults
	service tightvnc start

/etc/xrdp/startwm.sh : makefile
	sed -i.bak '/^\. / s/^/#/' $@
	egrep '^x-window-manager' 2>/dev/null || echo 'x-window-manager --startup /usr/bin/pcmanfm' >> $@

/etc/network/interfaces : Makefile
	sed -i.bak '/wlan0/ d' $@
	egrep '^source' 2>/dev/null || echo 'source /etc/network/interfaces.d/*.conf' >> $@

/etc/dhcp/dhcpd.conf : edits/dhcpd.conf Makefile
	sed -i.bak '/^subnet 192\.168\.99\.0 /,99 d' $@
	cat $< >> $@

.PHONY : packages
packages :
	if [ "$(packages_needed)" != '' ]; then apt-get install $(packages_needed); fi