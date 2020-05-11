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
  $AwsProfile
)

# Exit on first error
$ErrorActionPreference = "Stop"

Write-Host "Running NetworksExecutePackerBuild.ps1 script..."
Write-Host "Parameters:"
Write-Host "  $PackerBuilder"
Write-Host "  $PackerTemplate"
Write-Host "  $VarsFiles"
Write-Host "  $AwsProfile"

################################################################
$BoxFile = "rch-centos7-v$Env:BOX_VERSION.box"
$BoxUrl="https://richardcrouch.s3-eu-west-1.amazonaws.com/boxes/rch-centos7/$BoxFile"
#$PackerBinary = "c:\packer\packer_v1.5.6.exe"
$PackerBinary = "/usr/local/bin/packer"
################################################################

& $PackerBinary version
$PSversion = $PSVersionTable.PSVersion.Major
Write-Host "PowerShell version : $PSversion"

$Env:PACKER_LOG = "1"
Write-Host "PACKER_LOG : $Env:PACKER_LOG"

$WorkingDir = [string](Get-Location)
$Env:PACKER_LOG_PATH =  $WorkingDir + "\" +"$PackerBuilder.log"

Write-Host "WorkingDir is $WorkingDir"
Write-Host "PACKER_LOG_PATH : $Env:PACKER_LOG_PATH"
Write-Host "Env: BOX_VERSION                : $Env:BOX_VERSION"
Write-Host "Env: BOX_DESCRIPTION            : $Env:BOX_DESCRIPTION"
Write-Host "Env: Jenkins JOB_NAME           : $Env:JOB_NAME"
Write-Host "Env: Jenkins BUILD_DISPLAY_NAME : $Env:BUILD_DISPLAY_NAME"

[string]$BuildDate = Get-Date -uformat "%d-%m-%Y"
[string]$BoxDescription = $Env:BOX_DESCRIPTION +`
", built " + $BuildDate + `
"on Node " + $Env:NODE_NAME + `
", Jenkins Job=" + $Env:JOB_NAME + `
", Jenkins Build=" + $Env:BUILD_DISPLAY_NAME

Write-Host "BoxDescription : $BoxDescription"

$BoxVarsFile = Get-Content 'box-vars-template.json' -Raw
$BoxVarsFile = $BoxVarsFile.Replace("<box_version>",$Env:BOX_VERSION)
$BoxVarsFile = $BoxVarsFile.Replace("<box_description>",$BoxDescription)
$BoxVarsFile | out-file -filepath 'box-vars.json' -Encoding Ascii -Force
Write-Host "Populated box-vars.json to be passed to Packer is :"
Get-Content 'box-vars.json'

$validateargs = @('validate')

#packer build -var 'app_name_cmd_var=apache' apache.json
$args = @('build')
$args += "--only=$PackerBuilder"
$args += "-var-file=box-vars.json"  # pass the box version and description via var-file

$VarFiles = $VarsFiles -split ';'
foreach ($VarFile in $VarFiles){
    $args += "-var-file=$VarFile"
    $validateargs += "-var-file=$VarFile"
}

$args += $PackerTemplate
$validateargs += $PackerTemplate

# Step 0 : Run Packer in validation mode...
Write-Host "Validating the Packer template with the following arguments :"
Write-Host $validateargs
& $PackerBinary $validateargs

# Step 1 : Run Packer...
Write-Host "Running $PackerBinary with the following arguments :"
Write-Host $args
& $PackerBinary $args
$PackerExitCode = $LastExitCode
Write-Host "ExitCode from Packer Build : $PackerExitCode"

# Step 2 : Generate VirtualBox metadata.json file containing the version information
$TemplateFile = 'box-metadata-template.json'

$BoxChecksum = Get-FileHash -Path $BoxFile -Algorithm "SHA1"
$BoxChecksum = $BoxChecksum.Hash

$MetadataFile = Get-Content $TemplateFile -Raw
$MetadataFile=$MetadataFile.Replace("<version>",$Env:BOX_VERSION)
$MetadataFile=$MetadataFile.Replace("<checksum>",$BoxChecksum)
$MetadataFile=$MetadataFile.Replace("<description>",$BoxDescription)
$MetadataFile=$MetadataFile.Replace("<box_url>",$BoxUrl)

# Dump metadata.json to console
Write-Host "VBox-format metadata.json file :"
$MetadataFile

# Save to file so can be sent to S3 and collected as an artifact
$MetadataFile | out-file -filepath metadata.json -Encoding Ascii -Force

# If the Packer Build failed then fail the job
exit $PackerExitCode
