<?php
// For version information, look at the footer of this page

if (isset($_POST["submit"] )) {
    session_start();
    
    // CHANGE 1 : Choose one client
    $client      = "index.php"; 	        // Live

    $scenario    = $_POST['scenario'];      // mainly used for carry info during acceptance tests
    $domain      = $_POST['domain'];
    $email       = $_POST['email'];
    $person      = $_POST['person'];
    $company     = $_POST['company'];
    $ccemail     = $_POST['ccemail'];
    $industry    = $_POST['industry'];
    $country     = $_POST['country'];
    $cryptpin    = $_POST['cryptpin'];
    $emailownage = $_POST['emailownage'];
    $vulns       = False;
    $comply      = $_POST['comply'];
    $tag         = "webui";
    $allhosts    = $_POST['allhosts'];
    
    // Stuff below here is possibly legacy and should be removed at next maintenance cycle
    $mwc         = $_POST['mwc'];
    $nmap        = $_POST['nmap'];
    $debug       = $_POST['debug'];
    $subdomains  = $_POST['subdomains'];
    $dnsenum     = $_POST['dnsenum'];		

    $url = 'http://127.0.0.1:5001/tradr/v1.0/researchreport';

    $data = array('scenario' => $scenario, 'tag' => $tag, 'domain' => $domain, 'email' => $email, 'industry' => $industry, 'country' => $country , 'client' => $client, 'ccemail' => $ccemail, 'mwc' => $mwc, 'company' => $company, 'person' => $person, 'nmap' => $nmap, 'debug' => $debug, 'dnsenum' => $dnsenum, 'cryptpin' => $cryptpin, 'emailownage' => $emailownage, 'subdomains' => $subdomains, 'vulns' => $vulns, 'comply' => $comply, 'allhosts' => $allhosts);
    
    $options = array(
        'http' => array(
                'header' => "Content-type: application/x-www-form-urlencoded\r\n",
                'method' => 'POST',
                'content' => http_build_query($data),
               )
            );                                                                                                                                                      
    
    $context = stream_context_create($options);
    $result  = file_get_contents($url, false, $context);
    
    $jobId = $result;     // Flask returns False if a problem occurred                                                                                                                                                                                                                      
    
    // store critical info so it can be referenced from other PHP pages
    $_SESSION['jobId']      = $jobId;
    $_SESSION['domain']     = $domain;
    $_SESSION['email']      = $email;
    $_SESSION['ccemail']    = $ccemail;
    $_SESSION['company']    = $company;
    $_SESSION['person']     = $person;
    $_SESSION['subdomains'] = $subdomains;
    $_SESSION['vulns']      = $vulns;
    $_SESSION['allhosts']   = $allhosts;
        
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
    <meta name="description" content="Reveal">
    <meta name="author" content="TRADR">
    <!-- Change 2 : Modify title to be Reveal Verify or Reveal Verify-STAGE or Reveal Verify-QA -->
    <title>TRADR</title>
    <link rel="stylesheet" href="bootstrap.min.css">
	<link rel="stylesheet" type="text/css" href="verify-webui.css"/>
  
  <script>
    function domainFill() {
      var str = document.getElementById("email").value;
      var res = str.substr(str.indexOf("@") + 1);
      document.getElementById("domain").value = res;
    }
  </script>
  
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
  				<!-- Change 3 : Add or remove (STAGE or QA) from the text below -->
  				<h3 class="page-header text-center"><i>TRADR</i></h3>
				<div class="intro_message">
					Generate TRADR Research Report.<br><br>
				</div>	
				<form class="form-horizontal" role="form" method="post" action="index.php">
					<div class="form-group">
						<label for="person" class="col-sm-3 control-label">Your Name</label>
						<div class="col-sm-8">
							<input type="text" class="form-control" id="person" name="person" maxlength="40" pattern="^[\x00-\x7F]+$" data-toggle="tooltip" title="Enter the name of the person requesting the Report" placeholder="Person requesting the Report" required>
						</div>
					</div>

					<div class="form-group">
						<label for="email" class="col-sm-3 control-label">Your Email</label>
						<div class="col-sm-7">
							<input type="email" class="form-control" id="email" name="email" onChange="domainFill()" data-toggle="tooltip" title="The Report will be sent to this email address" placeholder="Email to receive the Report" value="<?php echo htmlspecialchars($_POST['email']);?>" pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,3}$" required oninvalid="setCustomValidity('Please enter a valid email address')" oninput="setCustomValidity('')">
						</div>
					</div>
					<div class="form-group">
						<label for="name" class="col-sm-3 control-label">Tickers</label>
						<div class="col-sm-7">
							<input type="text" class="form-control" id="ticker_list" name="ticker_list" maxlength="40" data-toggle="tooltip" pattern="[A-Za-z0-9._%+-]+\.[a-z\s]{2,3}$" title="Enter the ticker(s) for which the assessment is required, e.g. AMZN" placeholder="Ticker or comma-separated list" value="<?php echo htmlspecialchars($_POST['ticker_list']);?>" required oninvalid="setCustomValidity('Please enter a valid ticker list.')" oninput="setCustomValidity('')">
						</div>
					</div>
					<!--
					<div class="form-group">
						<label for="cryptopin" class="col-sm-3 control-label">Report Encryption Password</label>
						<div class="col-sm-4">
                            <input type="password" class="form-control" id="cryptpin" name="cryptpin" maxlength="16" pattern="[A-Za-z0-9\s]+"  placeholder="Upto 16 chars" data-toggle="tooltip" title="Entering a password in this field will cause the Passive Vulnerability Report to be encrypted. The password can be upto 16 characters long and can include numbers and letters but not special characters such as spaces." oninvalid="setCustomValidity('Please enter an alphanumeric password. (Maximium 16 characters)')" oninput="setCustomValidity('')">
					            <script>
                                    document.getElementById('cryptpin').value = '123456';
                                </script>
                                        
                                        </div>
					</div>
					<div class="form-group">
						<label for="email" class="col-sm-3 control-label">CC: Email</label>
						<div class="col-sm-7">
							<input type="email" class="form-control" id="ccemail" name="ccemail" data-toggle="tooltip" title="Additional Email address to receive the Report" placeholder="Additional Email to receive Assessment" value="<?php if(isset($_POST['submit'] )) {  echo htmlspecialchars($_POST['ccemail']); } ?>">
							    <script>
						            document.getElementById('ccemail').value = '';
						        </script>
						</div>
					</div>
					-->
					<hr>
					<!--
					<div class="form-group">
						<label for="comply" class="col-md-8 control-label">Add <em>Reve@l:Comply</em> ISO27002 Control(s) Recommendations</label>
						<div class="col-md-1">
							<input type="checkbox" id="checkbox" value="TRUE" class="form-control" name="comply" checked data-toggle="tooltip" title="Enabling this will include ISO27002 Control information in the Report">
						</div>
					</div>
					<div class="form-group">
						<label for="dnsenum" class="col-md-8 control-label">Use hostnames from DNS OSINT</label>
						<div class="col-md-1">
							<input type="checkbox" id="checkbox" value="TRUE" class="form-control" name="dnsenum" checked data-toggle="tooltip" title="Enabling this will use DNS subdomains from OSINT sources. This generally always markedly increases the number of hosts that are included in the Report">
						</div>
					</div>

					<div class="form-group">
						<label for="dnsenum" class="col-md-6 control-label">Do NOT bruteforce DNS subdomains</label>
						<div class="col-md-1">
							<input type="radio" id="optionsRadio1" value="none" class="form-control" name="dnsenum">
						</div>
						<label for="dnsenum" class="col-md-6 control-label">Bruteforce subdomains (&lt;= 1 min)</label>
						<div class="col-md-1">
							<input type="radio" id="optionsRadio2" value="dnslite" class="form-control" name="dnsenum" checked>
						</div>
						<label for="dnsenum" class="col-md-6 control-label">Bruteforce subdomains (&lt;= 15 mins)</label>
						<div class="col-md-1">
							<input type="radio" id="optionsRadio3" value="dnsstandard" class="form-control" name="dnsenum">
						</div>
						<label for="dnsenum" class="col-md-6 control-label">Bruteforce subdomains (No time limit)</label>
						<div class="col-md-1">
							<input type="radio" id="optionsRadio4" value="dnsfull" class="form-control" name="dnsenum">
						</div>
					</div>
					-->
					<!--
					<div class="form-group">
						<label for="emailownage" class="col-md-8 control-label">Breached Accounts Information</label>
						<div class="col-md-1">
							<input type="checkbox" id="checkbox" value="TRUE" class="form-control" name="emailownage" checked data-toggle="tooltip" title="Enabling this will include email addresses from domains that have been leaked as part of a data breach">
						</div>
					</div>
					<div class="form-group">
						<label for="allhosts" class="col-md-8 control-label">Include All Hosts/Accounts in Report</label>
						<div class="col-md-1">
							<input type="checkbox" id="checkbox" value="TRUE" class="form-control" name="allhosts" checked data-toggle="tooltip" title="Enabling this will add all available hosts/breached accounts information to the Report">
						</div>
					</div>
					<hr>
					<div class="form-group">
						<label for="consent" class="col-md-8 control-label">I agree to the Terms & Conditions</label>
						<div class="col-md-1">
							<input type="checkbox" id="checkbox" value="TRUE" class="form-control" name="consent" data-toggle="tooltip" title="You must consent to the Terms and Conditions" required>
						</div>
					</div>
					-->
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
	<!---
	<footer class="footer"><div class="container"><p>(c) 2024 : TRADR v0.0.1</p></div></footer>
	-->
    <script src="jquery.min.js"></script>
    <script src="bootstrap.min.js"></script>
  </body>
</html>
