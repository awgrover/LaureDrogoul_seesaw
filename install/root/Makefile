rcdirs := $(shell /bin/ls -d /etc/rc?.d | grep -v rcS.d)

.PHONY : setup
setup : $(rcdirs) start_vnc
	@echo "cd /etc/network/interfaces.d" echo "./pick *something*"

$(rcdirs): /etc/init.d/tightvnc
    update-rc.d tightvnc defaults

.PHONY : 
start_vnc :
    ps -C Xtightvnc || service tightvnc start

/etc/rc2.d/*.
update-rc
./etc/init.d/tightvnc
