#!/bin/sh

# Bashscript which is executed by bash *AFTER* complete installation is done
# (but *BEFORE* postupdate). Use with caution and remember, that all systems
# may be different! Better to do this in your own Pluginscript if possible.
#
# Exit code must be 0 if executed successfull.
#
# Will be executed as user "loxberry".
#
# We add 5 arguments when executing the script:
# command <TEMPFOLDER> <NAME> <FOLDER> <VERSION> <BASEFOLDER>
#
# For logging, print to STDOUT. You can use the following tags for showing
# different colorized information during plugin installation:
#
# <OK> This was ok!"
# <INFO> This is just for your information."
# <WARNING> This is a warning!"
# <ERROR> This is an error!"
# <FAIL> This is a fail!"

# To use important variables from command line use the following code:
ARGV0=$0 # Zero argument is shell command
#echo "<INFO> Command is: $ARGV0"

ARGV1=$1 # First argument is temp folder during install
#echo "<INFO> Temporary folder is: $ARGV1"

ARGV2=$2 # Second argument is Plugin-Name for scipts etc.
#echo "<INFO> (Short) Name is: $ARGV2"

ARGV3=$3 # Third argument is Plugin installation folder
#echo "<INFO> Installation folder is: $ARGV3"

ARGV4=$4 # Forth argument is Plugin version
#echo "<INFO> Installation folder is: $ARGV4"

ARGV5=$5 # Fifth argument is Base folder of LoxBerry
#echo "<INFO> Base folder is: $ARGV5"

DOINSTALLFILE=$ARGV5/data/plugins/$ARGV3/doinstall
touch $DOINSTALLFILE
PATHTODATA=$ARGV5/data/plugins/$ARGV3
/bin/sed -i "s:REPLACEBYPATHTODATA:$PATHTODATA:" $ARGV5/system/daemons/plugins/$ARGV2

# VM Detection
RPi_or_not=`cat /proc/cpuinfo|grep "model name"|grep "ARM"|wc -l`
if [ -z ${RPi_or_not+x} ]
then 
  	echo "<INFO> *************************************************************"
   	echo "<INFO> * Can not detect the Hardware. Please be informed, that the *"
	  echo "<INFO> * RPi Monitor is not fully working on a virtualized Machine *"
	  echo "<INFO> * In any case you must reboot to start the RPi-Monitor      *"
	  echo "<INFO> *************************************************************"
else 
	if [[ "$RPi_or_not" == 0 ]]
	then
  	echo "<INFO> *************************************************************"
	  echo "<INFO> * RPi Monitor is not fully working on a virtualized Machine *"
	  echo "<INFO> * In any case you must reboot to start the RPi-Monitor      *"
	  echo "<INFO> *************************************************************"
  else
  	echo "<INFO> ******************************************"
	  echo "<INFO> * Please reboot to start the RPi-Monitor *"
	  echo "<INFO> ******************************************"
  fi

# Exit with Status 0
exit 0
