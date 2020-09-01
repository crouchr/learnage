<?php
// For version information, look at the footer of this page

if (isset($_POST["submit"] )) {
    session_start();

    $client      = "DEV-index.php"; 	    // indicate what generated the POST request

    $scenario    = $_POST['scenario'];      // mainly used for carry info during acceptance tests
    $pressure    = $_POST['pressure'];
    $ptrend      = $_POST['ptrend'];
    $wind_dir    = $_POST['wind_dir'];
    $bforecast   = $_POST['bforecast'];
    $clouds      = $_POST['clouds'];
    $yest_rain   = $_POST['yest_rain'];
    $yest_wind   = $_POST['yest_wind'];
    $notes       = $_POST['notes'];
    $email       = $_POST['email'];

    $url = 'http://127.0.0.1:5001/ensight/v1.0/doscan';
    $url = 'http://192.168.1.15:5001/getmetinfo';

    $data = array(
        'scenario'  => $scenario,
        'pressure'  => $pressure,
        'ptrend'    => $ptrend,
        'wind_dir'  => $wind_dir,
        'bforecast' => $bforecast,
        'clouds'    => $clouds,
        'yest_rain' => $yest_rain,
        'yest_wind' => $yest_wind,
        'notes'     => $notes,
        'email'     => $email,
        );

    $options = array(
        'http' => array(
                'header' => "Content-type: application/x-www-form-urlencoded\r\n",
                'method' => 'POST',
                'content' => http_build_query($data),
               )
            );                                                                                                                                                      
    
    $context = stream_context_create($options);
    $result  = file_get_contents($url, false, $context);
    
    $jobId = $result;       // Flask returns False if a problem occurred
    
    // store critical info so it can be referenced from other PHP pages
    $_SESSION['pressure']  = $pressure;
    $_SESSION['ptrend']    = $ptrend;
    $_SESSION['wind_dir']  = $wind_dir;
    $_SESSION['bforecast'] = $bforecast;
    $_SESSION['clouds']    = $clouds;
    $_SESSION['yest_rain'] = $yest_rain;
    $_SESSION['yest_wind'] = $yest_wind;
    $_SESSION['notes']     = $notes;
    $_SESSION['email']     = $email;

    if ($jobId == False) {
        header("Location: failure.php"); # force HTTP redirect
    } else {
        header("Location: success.php");
    }  
}

?>

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="MetMini">
    <meta name="author" content="MetMini">
    <link rel="stylesheet" href="bootstrap.min.css">
	<link rel="stylesheet" type="text/css" href="webui.css"/>
    <title>MetMini</title>
  </head>
  
  <body>
  <script>
  $(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
    });
  </script>
  	<div class="container">
  		<div class="row">
  			<div class="col-md-6 col-md-offset-3">
  				<!-- Change 3 : Add or remove (STAGE) or (QA) from the text below -->
  				<h3 class="page-header text-center"><i>MetMini</i></h3>

				<div class="intro_message">
				    Enter basic meteorological information at 09:00 UTC and receive a forecast by email
				</div>

				<form class="form-horizontal" role="form" method="post" action="index.php">
					<div class="form-group">
						<label for="pressure" class="col-sm-3 control-label">Barometric Pressure (mbar)</label>
						<div class="col-sm-2">
							<input type="text" class="form-control" id="pressure" name="pressure" data-toggle="tooltip" title="Enter current barometric pressure" placeholder="Pressure" required>
								<script>
						            document.getElementById('pressure').value = '1013';
						        </script>
						</div>
					</div>

                    <div class="form-group">
					  <label for="ptrend" class="col-sm-3 control-label">Pressure Trend</label>
					  <div class="col-sm-3">
					    <select class="form-control" id="ptrend" name="ptrend" data-toggle="tooltip" title="Pressure Trend">
					      <option>Rising</option>
					      <option>Steady</option>
					      <option>Falling</option>
					      </select>
					  </div>
					</div>

					<div class="form-group">
					  <label for="wind_dir" class="col-sm-3 control-label">Wind Quadrant</label>
					  <div class="col-sm-2">
					    <select class="form-control" id="wind_dir" name="wind_dir" data-toggle="tooltip" title="Quadrant from where wind is currently blowing">
					      <option>NE</option>
					      <option>SE</option>
					      <option>SW</option>
					      <option>NW</option>
					    </select>  
					  </div>             
					</div>

					<div class="form-group">
					  <label for="bforecast" class="col-sm-3 control-label">Bresser Forecast Icon</label>
					  <div class="col-sm-4">
					    <select class="form-control" id="bforecast" name="bforecast" data-toggle="tooltip" title="Bresser forecast">
					      <option>Sunny</option>
					      <option>Slightly Cloudy</option>
					      <option>Cloudy</option>
					      <option>Rainy</option>
					      <option>Stormy</option>
					      <option>Snowy</option>
					      </select>
					  </div>
					</div>

					<div class="form-group">
						<label for="clouds" class="col-sm-3 control-label">Cloud Description</label>
						<div class="col-sm-8">
							<input type="text" class="form-control" id="clouds" name="clouds" maxlength="40" pattern="^[\x00-\x7F]+$" data-toggle="tooltip" title="Enter description of clouds, e.g. type, % coverage" placeholder="Clouds"  required>
								<script>
						            document.getElementById('clouds').value = 'None';
						        </script>
						</div>
					</div>

					<div class="form-group">
						<label for="yest_rain" class="col-sm-3 control-label">Yesterday Rain mm</label>
						<div class="col-sm-3">
							<input type="text" class="form-control" id="yest_rain" name="yest_rain" maxlength="40" pattern="^[\x00-\x7F]+$" data-toggle="tooltip" title="Enter Yesterday's Rainfall" placeholder="Rain" required>
								<script>
						            document.getElementById('yest_rain').value = '0';
						        </script>
						</div>
					</div>

					<div class="form-group">
						<label for="yest_wind" class="col-sm-3 control-label">Yesterday Wind</label>
						<div class="col-sm-3">
							<input type="text" class="form-control" id="yest_wind" name="yest_wind" maxlength="40" pattern="^[\x00-\x7F]+$" data-toggle="tooltip" title="Enter Yesterday's Wind" placeholder="Wind" required>
								<script>
						            document.getElementById('yest_wind').value = '0';
						        </script>
						</div>
					</div>

					<div class="form-group">
						<label for="notes" class="col-sm-3 control-label">Notes</label>
						<div class="col-sm-8">
							<input type="text" class="form-control" id="notes" name="notes" maxlength="40" pattern="^[\x00-\x7F]+$" data-toggle="tooltip" title="Enter any additional notes" placeholder="Notes" required>
								<script>
						            document.getElementById('notes').value = 'None';
						        </script>
						</div>
					</div>

					<div class="form-group">
						<label for="email" class="col-sm-3 control-label">Your Email</label>
						<div class="col-sm-7">
							<input type="email" class="form-control" id="email" name="email" onChange="domainFill()" data-toggle="tooltip" title="Forecast will be sent to this email address" placeholder="Email to receive the Forecast" value="<?php echo htmlspecialchars($_POST['email']);?>" pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,3}$" required oninvalid="setCustomValidity('Please enter a valid email address')" oninput="setCustomValidity('')">
								<script>
						            document.getElementById('email').value = 'richard.crouch100@gmail.com';
						        </script>
						</div>
					</div>

					<div class="form-group">
						<div class="col-sm-8 col-sm-offset-1">
							<input id="submit" name="submit" type="submit" value="Submit" class="btn btn-primary">
						</div>
					</div>
                         		<div class="form-group">
						<div class="col-sm-10 col-sm-offset-2">
							<?php echo $result; ?>	
						</div>
						<input type="hidden" value="None" name="scenario"/>
					</div>
				</form> 
				</div>
			</div>
		</div>
	</div>
	<footer class="footer"><div class="container"><p>(c) 2020 MetMini v0.0.1</p></div></footer>
    <script src="jquery.min.js"></script>
    <script src="bootstrap.min.js"></script>
  </body>
</html>
