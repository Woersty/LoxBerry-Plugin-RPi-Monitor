#!/usr/bin/perl

# Copyright 2016 Michael Schlenstedt, michael@loxberry.de
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


##########################################################################
# Modules
##########################################################################

use LoxBerry::System;
use LoxBerry::Web;
use LoxBerry::Log;
use MIME::Base64;
use List::MoreUtils 'true','minmax';
use HTML::Entities;
use CGI::Carp qw(fatalsToBrowser);
use CGI qw/:standard/;
use Config::Simple '-strict';
use warnings;
use strict;
no  strict "refs"; 

# Variables
our @pluginconfig_strings 		= ('DPORT');
our $DPORT="8888";
my $maintemplatefilename 		= "rpi_monitor.html";
my $errortemplatefilename 		= "error.html";
my $successtemplatefilename 	= "success.html";
my $helptemplatefilename		= "help.html";
my $pluginconfigfile 			= "RPi-Monitor.cfg";
my $languagefile 				= "language.ini";
my $logfile 					= "RPi-Monitor.log";
my $template_title;
my $no_error_template_message	= "<b>RPi-Monitor:</b> The error template is not readable. We must abort here. Please try to reinstall the plugin.";
my $version 					= LoxBerry::System::pluginversion();
my $helpurl 					= "http://www.loxwiki.eu/display/LOXBERRY/RPi-Monitor";
my $log 							= LoxBerry::Log->new ( name => 'RPi-Monitor', filename => $lbplogdir ."/". $logfile, append => 1 );
my $plugin_cfg 					= new Config::Simple($lbpconfigdir . "/" . $pluginconfigfile);
my %Config 						= $plugin_cfg->vars() if ( $plugin_cfg );
our $error_message				= "";

# Logging
my $plugin = LoxBerry::System::plugindata();

##########################################################################
# Read Settings
##########################################################################

# Version of this script
$version = "2020.03.22";

# Logging
my $plugin = LoxBerry::System::plugindata();


$LoxBerry::System::DEBUG 	= 1 if $plugin->{PLUGINDB_LOGLEVEL} eq 7;
$LoxBerry::Web::DEBUG 		= 1 if $plugin->{PLUGINDB_LOGLEVEL} eq 7;
$log->loglevel($plugin->{PLUGINDB_LOGLEVEL});

LOGDEB "Init CGI and import names in namespace R::";
my $cgi 	= CGI->new;
$cgi->import_names('R');

LOGDEB "Get language";
my $lang	= lblanguage();
LOGDEB "Resulting language is: " . $lang;

LOGDEB "Check, if filename for the errortemplate is readable";
stat($lbptemplatedir . "/" . $errortemplatefilename);
if ( !-r _ )
{
	LOGDEB "Filename for the errortemplate is not readable, that's bad";
	$error_message = $no_error_template_message;
	LoxBerry::Web::lbheader($template_title, $helpurl, $helptemplatefilename);
	print $error_message;
	LOGCRIT $error_message;
	LoxBerry::Web::lbfooter();
	LOGCRIT "Leaving RPi-Monitor Plugin due to an unrecoverable error";
	exit;
}

LOGDEB "Filename for the errortemplate is ok, preparing template";
my $errortemplate = HTML::Template->new(
		filename => $lbptemplatedir . "/" . $errortemplatefilename,
		global_vars => 1,
		loop_context_vars => 1,
		die_on_bad_params=> 0,
		associate => $cgi,
		%htmltemplate_options,
		debug => 1,
		);
LOGDEB "Read error strings from " . $languagefile . " for language " . $lang;
my %ERR = LoxBerry::System::readlanguage($errortemplate, $languagefile);

LOGDEB "Check, if filename for the successtemplate is readable";
stat($lbptemplatedir . "/" . $successtemplatefilename);
if ( !-r _ )
{
	LOGDEB "Filename for the successtemplate is not readable, that's bad";
	$error_message = $ERR{'ERRORS.ERR_SUCCESS_TEMPLATE_NOT_READABLE'};
	&error;
}
LOGDEB "Filename for the successtemplate is ok, preparing template";
my $successtemplate = HTML::Template->new(
		filename => $lbptemplatedir . "/" . $successtemplatefilename,
		global_vars => 1,
		loop_context_vars => 1,
		die_on_bad_params=> 0,
		associate => $cgi,
		%htmltemplate_options,
		debug => 1,
		);
LOGDEB "Read success strings from " . $languagefile . " for language " . $lang;
my %SUC = LoxBerry::System::readlanguage($successtemplate, $languagefile);

LOGDEB "Check, if filename for the maintemplate is readable, if not raise an error";
$error_message = $ERR{'ERRORS.ERR_MAIN_TEMPLATE_NOT_READABLE'};
stat($lbptemplatedir . "/" . $maintemplatefilename);
&error if !-r _;
LOGDEB "Filename for the maintemplate is ok, preparing template";
my $maintemplate = HTML::Template->new(
		filename => $lbptemplatedir . "/" . $maintemplatefilename,
		global_vars => 1,
		loop_context_vars => 1,
		die_on_bad_params=> 0,
		%htmltemplate_options,
		debug => 1
		);
LOGDEB "Read main strings from " . $languagefile . " for language " . $lang;
my %L = LoxBerry::System::readlanguage($maintemplate, $languagefile);

LOGSTART $L{'LOGMESSAGES.PLUGIN_CALL_START'};

LOGDEB "Check if plugin config file is readable";
if (!-r $lbpconfigdir . "/" . $pluginconfigfile) 
{
	LOGWARN "Plugin config file not readable.";
	LOGDEB "Check if config directory exists. If not, try to create it. In case of problems raise an error";
	$error_message = $ERR{'ERRORS.ERR_CREATE_CONFIG_DIRECTORY'};
	mkdir $lbpconfigdir unless -d $lbpconfigdir or &error; 
	LOGDEB "Try to create a default config";
	$error_message = $ERR{'ERRORS.ERR_CREATE CONFIG_FILE'};
	open my $configfileHandle, ">", $lbpconfigdir . "/" . $pluginconfigfile or &error;
		print $configfileHandle "[RPiMonitor]\nDPORT=".$DPORT."\n\n";
	close $configfileHandle;
	LOGWARN "Default config created. Display error anyway to force a page reload";
	$error_message = $ERR{'ERRORS.ERR_NO_CONFIG_FILE'};
	&error; 
}

LOGDEB "Parsing valid config variables into the maintemplate";
foreach my $config_value (@pluginconfig_strings)
{
	${$config_value} = $Config{'RPiMonitor.' . $config_value};
	if (defined ${$config_value} && ${$config_value} ne '') 
	{
  		LOGDEB "Set config variable: " . $config_value . " to " . ${$config_value};
  		$maintemplate->param($config_value	, ${$config_value} );
	}                                  	                             
	else
	{
	  	LOGWARN "Config variable: " . $config_value . " missing or empty.";     
  		$maintemplate->param($config_value	, "");
	}
}    
$maintemplate->param( "LBPPLUGINDIR" , $lbpplugindir);

LOGDEB "Call default page";
&defaultpage;

#####################################################
# Subs
#####################################################

sub defaultpage 
{
	LOGDEB "Sub defaultpage";
	LOGDEB "Set page title, load header, parse variables, set footer, end";
	$template_title = $L{'RPIMonitor.MY_NAME'};
	LoxBerry::Web::lbheader($template_title, $helpurl, $helptemplatefilename);
	$maintemplate->param( "rpi_monitor_url"		, "http://".$ENV{'HTTP_HOST'}.":".$DPORT."/");
	$maintemplate->param("HTMLPATH" => "/plugins/".$lbpplugindir."/");
	$maintemplate->param( "VERSION"			, $version);
  $maintemplate->param( "LOGLEVEL" 				, $plugin->{PLUGINDB_LOGLEVEL});
	$maintemplate->param( "PLUGINDB_MD5_CHECKSUM"	, $plugin->{PLUGINDB_MD5_CHECKSUM});
	$lbplogdir =~ s/$lbhomedir\/log\///; # Workaround due to missing variable for Logview
	$maintemplate->param( "LOGFILE" , $lbplogdir . "/" . $logfile );
	LOGDEB "Check for pending notifications for: " . $lbpplugindir . " " . $L{'RPIMonitor.MY_NAME'};
	my $notifications = LoxBerry::Log::get_notifications_html($lbpplugindir, $L{'RPIMonitor.MY_NAME'});
	LOGDEB "Notifications are:\n".encode_entities($notifications) if $notifications;
	LOGDEB "No notifications pending." if !$notifications;
  $maintemplate->param( "NOTIFICATIONS" , $notifications);
  print $maintemplate->output();
	LoxBerry::Web::lbfooter();
	LOGDEB "Leaving RPi-Monitor Plugin normally";
	LOGEND;
	exit;
}

sub error 
{
	LOGDEB "Sub error";
	LOGERR $error_message;
	LOGDEB "Set page title, load header, parse variables, set footer, end with error";
	$template_title = $ERR{'ERRORS.MY_NAME'} . " - " . $ERR{'ERRORS.ERR_TITLE'};
	LoxBerry::Web::lbheader($template_title, $helpurl, $helptemplatefilename);
	$errortemplate->param('ERR_MESSAGE'		, $error_message);
	$errortemplate->param('ERR_TITLE'		, $ERR{'ERRORS.ERR_TITLE'});
	$errortemplate->param('ERR_BUTTON_BACK' , $ERR{'ERRORS.ERR_BUTTON_BACK'});
	print $errortemplate->output();
	LoxBerry::Web::lbfooter();
	LOGERR "Leaving RPi-Monitor Plugin due to an unrecoverable error";
}
