<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="MetMini">
<meta name="author" content="MetMini">
<title>MetMini Success Page QA</title>
<link rel="stylesheet" href="bootstrap.min.css">
</head>

<body>

<h3>Meteorological information was submitted OK</h3>

<?php
session_start();
$forecast_text = $_SESSION['forecast_text'];
$email = $_SESSION['email'];

echo "<br>";
echo "<h4>Forecast : $forecast_text</h4>";
echo "<br>";
echo "<h4>Report will be sent to : $email</h4>";
?>
<br> 
You should receive a weather forecast email within the next few seconds.<br>
<br>
<a href="http://192.168.1.95/index.php">Perform another meteorological data collection</a><br>
<br>
(c) 2020 MetMini
</body>
</html>
