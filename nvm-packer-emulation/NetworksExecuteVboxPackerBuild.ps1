# Richard Crouch modified script to use for VirtualBox builds
# Added $BoxVersion and $BoxDescription as calling parameters as well as generation of metaadata.json

param (
  [Parameter(Mandatory)]
  $PackerBuilder,
  [Parameter(Mandatory)]
  $PackerTemplate,
  [Parameter(Mandatory)]
  $VarsFiles,
  [Parameter(Mandatory)]
  $AwsProfile,
  [Parameter(Mandatory)]
  $BoxVersion,
  [Parameter(Mandatory)]
  $BoxDescription
)

Write-Host "Running NetworksExecutePackerBuild.ps1 script..."
$PSversion = $PSVersionTable.PSVersion.Major
Write-Host "PowerShell version : $PSversion"

$Env:PACKER_LOG = "1"
Write-Host "PACKER_LOG : $Env:PACKER_LOG"

$WorkingDir = [string](Get-Location)
$PackerBinary = "c:\packer\packer_v1.5.6.exe"
$PackerBinary = "/usr/local/bin/packer"

$Env:PACKER_LOG_PATH =  $WorkingDir + "\" +"$PackerBuilder.log"

Write-Host "WorkingDir is $WorkingDir"
Write-Host "PACKER_LOG_PATH : $Env:PACKER_LOG_PATH"

#The AWS_PROFILE environment variable is used by AWS CLI\Packer to determine which profile to use in the AWS_SHARED_CREDENTIALS_FILE
<#$Env:AWS_PROFILE = $AwsProfile

# Unsetting these AWS access keys is a Jenkins-CI work-around.  In order to get the Github Access Token it is stored
# as a global password .. unfortunately, the developmentaws access keys are also a global password.  If set as ENV vars
# take precedence over the AWS_SHARED_CREDENTIALS_FILE env variable which is what we actually use for credentials.

If (Test-Path env:AWS_SECRET_ACCESS_KEY) { Remove-Item Env:AWS_SECRET_ACCESS_KEY }
If (Test-Path env:AWS_ACCESS_KEY_ID) { Remove-Item Env:AWS_ACCESS_KEY_ID }

$ProfilesUsingNonProd = "jenkins.development","jenkins.staging","developmentaws","nvm-staging","cct-sre-nonprod","cct-itg-ee"
$ProfilesUsingProd = "jenkins.emea","jenkins.global","nvm-ops","nvm-emea","nvm-global","cct-prd-sre"

If ( $ProfilesUsingNonProd -contains $AwsProfile) {
    $Env:AWS_SHARED_CREDENTIALS_FILE = $Env:NON_PRODUCTION_SHARED_CREDENTIALS_FILE
    Write-Host "Using Non-Production AWS shared credentials file"
}

ElseIf ( $ProfilesUsingProd -contains $AwsProfile)
    { $Env:AWS_SHARED_CREDENTIALS_FILE = $Env:PRODUCTION_SHARED_CREDENTIALS_FILE
    Write-Host "Using Production AWS shared credentials file"
}
Else {
    "The requested AWS profile $AwsProfile is not known by ExecutePackerBuild.ps1 script. Exiting..."
    exit 1
}#>

$BoxDescription = '{0} {1} for Job {2}' -f $BoxDescription $Get-Date $Env:JOB_NAME
$BoxDescription

$BoxVarsFile = Get-Content 'box-vars-template.json' -Raw
$BoxVarsFile = $BoxVarsFile.Replace("<box_version>",$BoxVersion)
$BoxVarsFile = $BoxVarsFile.Replace("<box_description>",$BoxDescription)
$BoxVarsFile
$BoxVarsFile | out-file -filepath 'box-vars.json'

$env:BUILD_NUMBER
#$BoxVersionArg = "box_version=$BoxVersion"
#$BoxVersionArg = "'" + $BoxVersionArg "'"
#$BoxDescriptionArg = "vm_description=$BoxDescription"
#$BoxVersionArg
#$BoxDescriptionArg

# RCH : $args += "--only=$PackerBuilder"
$validateargs = @('validate')

#packer build -var 'app_name_cmd_var=apache' apache.json
$args = @('build')
$args += "--only=virtualbox-iso"
$args += "--force"
$args += "-var-file=box-vars.json"
#$args += '-var "box_version=$BoxVersion"'
#$args += '-var "vm_description=$BoxDescription"'
#$args += "-var 'box_version=$BoxVersion'"
#$args += "-var 'vm_description=$BoxDescription'"
#$args += "-var $BoxVersionArg"
#$args += "-var $BoxDescriptionArg"

$VarFiles = $VarsFiles -split ';'
foreach ($VarFile in $VarFiles){
    $args += "-var-file=$VarFile"
    $validateargs += "-var-file=$VarFile"
}

$args += $PackerTemplate
$validateargs += $PackerTemplate

# Temporarily disabled during debugging as it takes 10 minutes to run
# Step 1 : Run Packer in validation mode...
#Write-Host "Validating the Packer var file(s) and template with the following arguments :"
#Write-Host $validateargs
#& $PackerBinary $validateargs

# Step 2 : Run Packer...
Write-Host "Running $PackerBinary with the following arguments :"
Write-Host $args
& $PackerBinary $args
$PackerExitCode = $LastExitCode
Write-Host "ExitCode from Packer Build : $PackerExitCode"

# Step 3 : Generate VirtualBox metadata.json file containing the version information
$TemplateFile = 'box-metadata-template.json'
$BoxFile = "CentOS7_virtualbox-v$BoxVersion.box"
$BoxUrl="http://boxfilerepo.s3-eu-west-1.amazonaws.com/$box_name"

$BoxChecksum = Get-FileHash -Path $BoxFile -Algorithm "SHA1"
$BoxChecksum = $BoxChecksum.Hash

# Dump to console
$BoxVersion
$BoxDescription

$BoxUrl="http://boxfilerepo.s3-eu-west-1.amazonaws.com/$box_name"

$MetadataFile = Get-Content $TemplateFile -Raw

$MetadataFile=$MetadataFile.Replace("<version>",$BoxVersion)
$MetadataFile=$MetadataFile.Replace("<checksum>",$BoxChecksum)
$MetadataFile=$MetadataFile.Replace("<description>",$BoxDescription)
$MetadataFile=$MetadataFile.Replace("<box_url>",$BoxUrl)

# Dump metadata.json to console
$MetadataFile

# Save to file so can be sent to S3 and collected as an artifact
$MetadataFile | out-file -filepath metadata.json

# If the Packer Build failed then fail the job
exit $PackerExitCode
