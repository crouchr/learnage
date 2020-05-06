[string]$Path = '/home/crouchr/PycharmProjects/learnage/powershell/template.txt'

$checksum = Get-FileHash -Path $Path -Algorithm "SHA1"
$checksum = $checksum.Hash
$checksum

$version="1.2.3"
$description="This is a useful box"
$box_name="CenOS7_virtualbox_v$version.box"
$box_url="http://boxfilerepo.s3-eu-west-1.amazonaws.com/$box_name" 

$template = Get-Content $Path -Raw

$template=$template.Replace("<version>",$version)
$template=$template.Replace("<checksum>",$checksum)
$template=$template.Replace("<description>",$description)
$template=$template.Replace("<box_url>",$box_url)

$template