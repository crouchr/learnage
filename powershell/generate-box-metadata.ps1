param(
    [Parameter(Mandatory)]
    $BoxVersion,
    [Parameter(Mandatory)]
    $BoxDescription
)

#[string]$Path = '/home/crouchr/PycharmProjects/learnage/powershell/template.txt'
[string]$Path = 'template.txt'
$checksum = Get-FileHash -Path $Path -Algorithm "SHA1"
$checksum = $checksum.Hash

$BoxVersion
$BoxDescription

#$version="1.2.3"
#$description="This is a useful box"
$box_name="CenOS7_virtualbox_v$BoxVersion.box"
$box_url="http://boxfilerepo.s3-eu-west-1.amazonaws.com/$box_name" 

$template = Get-Content $Path -Raw

$template=$template.Replace("<version>",$BoxVersion)
$template=$template.Replace("<checksum>",$checksum)
$template=$template.Replace("<description>",$BoxDescription)
$template=$template.Replace("<box_url>",$box_url)

$template