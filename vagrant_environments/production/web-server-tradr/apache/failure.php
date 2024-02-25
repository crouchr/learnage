<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="TRADR">
<meta name="author" content="TRADR">
<title>Report Failure Page LIVE</title>
<link rel="stylesheet" href="bootstrap.min.css">
</head>

<body>

<h3>Oops ! There was a problem generating a TRADR Research Report</h3>

<?php
session_start();

$domain = $_SESSION['ticker_list'];
echo "<h4>Ticker(s) to be assessed : $ticker_list</h4>";

$email = $_SESSION['email'];
echo "<h4>Report will be sent to : $email</h4>";

#$jobId = $_SESSION['jobId'];
#echo "<h4>Our reference : $jobId</h4>";

?>  
<br>
<!--
<a href="https://verify.sytelreply.com:443/verify/index.php">Go back to the start</a><br>
-->
<br>
(c)2024 TRADR
</body>
</html>
