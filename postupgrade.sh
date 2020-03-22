#!/bin/bash

ARGV1=$1 # First argument is temp folder during install
ARGV3=$3 # Third argument is Plugin installation folder
ARGV5=$5 # Fifth argument is Base folder of LoxBerry
shopt -s dotglob

echo "<INFO> Moving back existing config files"
mv -v /tmp/$ARGV1\_upgrade/config/* $ARGV5/config/plugins/$ARGV3/

echo "<INFO> Moving back existing log files"
mv -v /tmp/$ARGV1\_upgrade/log/* $ARGV5/log/plugins/$ARGV3/

echo "<INFO> Moving back existing template files"
mv -v /tmp/$ARGV1\_upgrade/rpitemplates/* /etc/rpimonitor/template/

echo "<INFO> Remove temporary folders"
rm -r /tmp/$ARGV1\_upgrade

# Exit with Status 0
exit 0
