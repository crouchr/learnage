<?php
# Test script for emulating an attackers script using RFI - See Glastopf KYT Paper
$un = @php_uname();
$up = system(uptime);

echo "uname -a: $un<br>";
echo "uptime: $up<br>";

?>