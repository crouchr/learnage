<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Sytel Reveal Cyber Tool">
<meta name="author" content="Sytel Reply">
<title>Reveal Verify Report Success Page LIVE</title>
<link rel="stylesheet" href="bootstrap.min.css">
</head>

<body>

<h3>Network Assessment Request was successfully submitted</h3>

<?php
session_start();

$domain = $_SESSION['domain'];
echo "<h4>IP network to be assessed : $domain</h4>";

$email = $_SESSION['email'];
echo "<h4>Report will be sent to : $email</h4>";

$jobId = $_SESSION['jobId'];
echo "<h4>Our reference : $jobId</h4>";

?>  
<br> 
You should receive a notification email within the next few seconds.<br>
Your Network Assessment Report should be emailed to you within 5-10 minutes.<br>
<br>
<a href="https://verify.sytelreply.com:443/verify/index.php">Perform another Network Assessment</a><br>
<br>
(c) 2017 Sytel Reply
</body>
</html>
