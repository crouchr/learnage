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

Write-Host "Running NetworksExecutePackerBuild.ps1 script..."

################################################################
$BoxFile = "CentOS7_virtualbox-v$Env:BOX_VERSION.box"
$BoxUrl="http://boxfilerepo.s3-eu-west-1.amazonaws.com/$BoxFile"
$PackerBinary = "c:\packer\packer_v1.5.6.exe"
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

$BoxDescription = "$Env:BOX_DESCRIPTION, built $(Get-Date), Job=$Env:JOB_NAME, Build=$Env:BUILD_DISPLAY_NAME"
$BoxDescription
$BoxVersion

$BoxVarsFile = Get-Content 'box-vars-template.json' -Raw
$BoxVarsFile = $BoxVarsFile.Replace("<box_version>",$Env:BOX_VERSION)
$BoxVarsFile = $BoxVarsFile.Replace("<box_description>",$BoxDescription)
$BoxVarsFile
$BoxVarsFile | out-file -filepath 'box-vars.json'

# RCH : $args += "--only=$PackerBuilder"
$validateargs = @('validate')

#packer build -var 'app_name_cmd_var=apache' apache.json
$args = @('build')
$args += "--only=virtualbox-iso"
$args += "--force"
$args += "-var-file=box-vars.json"

$VarFiles = $VarsFiles -split ';'
foreach ($VarFile in $VarFiles){
    $args += "-var-file=$VarFile"
    $validateargs += "-var-file=$VarFile"
}

$args += $PackerTemplate
$validateargs += $PackerTemplate

# Temporarily disabled during debugging as it takes 10 minutes to run
# Step 1 : Run Packer in validation mode...
Write-Host "Validating the Packer template with the following arguments :"
Write-Host $validateargs
& $PackerBinary $validateargs

# Step 2 : Run Packer...
Write-Host "Running $PackerBinary with the following arguments :"
Write-Host $args
& $PackerBinary $args
#$PackerExitCode = $LastExitCode
Write-Host "ExitCode from Packer Build : $PackerExitCode"

# Step 3 : Generate VirtualBox metadata.json file containing the version information
$TemplateFile = 'box-metadata-template.json'

$BoxChecksum = Get-FileHash -Path $BoxFile -Algorithm "SHA1"
$BoxChecksum = $BoxChecksum.Hash

$MetadataFile = Get-Content $TemplateFile -Raw
$MetadataFile=$MetadataFile.Replace("<version>",$Env:BOX_VERSION)
$MetadataFile=$MetadataFile.Replace("<checksum>",$BoxChecksum)
$MetadataFile=$MetadataFile.Replace("<description>",$BoxDescription)
$MetadataFile=$MetadataFile.Replace("<box_url>",$BoxUrl)

# Dump metadata.json to console
$MetadataFile

# Save to file so can be sent to S3 and collected as an artifact
$MetadataFile | out-file -filepath metadata.json

# If the Packer Build failed then fail the job
exit $PackerExitCode
