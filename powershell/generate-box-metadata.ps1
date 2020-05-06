param(
    [Parameter(Mandatory)]
    $BoxVersion,
    [Parameter(Mandatory)]
    $BoxDescription
)

$pwshversion

[string]$Path = 'box-metadata-template.txt'
$checksum = Get-FileHash -Path $Path -Algorithm "SHA1"
$checksum = $checksum.Hash

$BoxVersion
$BoxDescription

$box_name="CentOS7_virtualbox-v$BoxVersion.box"
$box_url="http://boxfilerepo.s3-eu-west-1.amazonaws.com/$box_name" 

$template = Get-Content $Path -Raw

$template=$template.Replace("<version>",$BoxVersion)
$template=$template.Replace("<checksum>",$checksum)
$template=$template.Replace("<description>",$BoxDescription)
$template=$template.Replace("<box_url>",$box_url)

# Dump to console
$template

# Save to file so can be sent to S3 and as an artifact
$template | out-file -filepath metadata.json

