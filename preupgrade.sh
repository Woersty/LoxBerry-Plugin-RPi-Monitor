#!/bin/sh
# To use important variables from command line use the following code:
ARGV1=$1 # First argument is temp folder during install
ARGV3=$3 # Third argument is Plugin installation folder
ARGV5=$5 # Fifth argument is Base folder of LoxBerry

echo "<INFO> Creating temporary folders for upgrading"
mkdir -p /tmp/$ARGV1\_upgrade/config
mkdir -p /tmp/$ARGV1\_upgrade/log
mkdir -p /tmp/$ARGV1\_upgrade/rpitemplates

echo "<INFO> Backing up existing config files"
mv -v $ARGV5/config/plugins/$ARGV3/* /tmp/$ARGV1\_upgrade/config/

echo "<INFO> Backing up existing log files"
mv -v $ARGV5/log/plugins/$ARGV3/* /tmp/$ARGV1\_upgrade/log/

echo "<INFO> Backing up existing templates"
cp -v /etc/rpimonitor/template/*.conf /tmp/$ARGV1\_upgrade/rpitemplates/

exit 0
