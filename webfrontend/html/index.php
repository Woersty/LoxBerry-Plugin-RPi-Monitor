<?php
require_once "loxberry_system.php"; 
$L						= LBSystem::readlanguage("language.ini");
$ini_array 		= parse_ini_file ( "$lbpconfigdir/RPi-Monitor.cfg" , TRUE , INI_SCANNER_NORMAL );
$host 				= $_SERVER["HTTP_HOST"];
$port 				= $ini_array["RPiMonitor"]["DPORT"];
$connection 	= @fsockopen($host, $port);
if (is_resource($connection))
{
    fclose($connection);
    header("Location: http://$host:$port/");
}
else
{
    echo '<h2>'.$L["PLUGIN.NOT_RESPONDING_ON_PORT"]. "http://" . $host . ':' . $port. "</h2>\n";
}
exit;