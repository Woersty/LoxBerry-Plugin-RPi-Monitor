echo "Installing/Reinstalling RPiMonitor package"
systemctl stop rpimonitor >/dev/null 2>&1
#dpkg -i REPLACELBPDATADIR/rpimonitor_2.12-r0_all.deb 
dpkg -i REPLACELBPDATADIR/rpimonitor_2.13-beta6_all.deb

set -x
cp REPLACELBPDATADIR/*.conf /etc/rpimonitor/template/
if [ -d "/tmp/rpi.save/" ]; then
	cp -f /tmp/rpi.save/*.conf /etc/rpimonitor/template/ 
fi
mkdir -p /tmp/rpi.save/
cp -f /etc/rpimonitor/template/*.conf /tmp/rpi.save/ 
rm -rf REPLACELBPDATADIR 
ln -s /etc/rpimonitor/template REPLACELBPDATADIR
cp -f /tmp/rpi.save/*.conf /etc/rpimonitor/template/ 
rm -rf /tmp/rpi.save >/dev/null 2>&1
chmod -R 755 REPLACELBPDATADIR
chown -R loxberry REPLACELBPDATADIR
chgrp -R loxberry REPLACELBPDATADIR
chmod -R 755 /etc/rpimonitor/template
chown -R loxberry /etc/rpimonitor/template
chgrp -R loxberry /etc/rpimonitor/template
set +x
/etc/init.d/rpimonitor update 
/etc/init.d/rpimonitor install_auto_package_status_update
echo "Calling RPiMonitor Daemon"
REPLACELBHOMEDIR/system/daemons/plugins/RPi-Monitor 

exit 0
