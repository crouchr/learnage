
# Check the permitted IPs for /Auth/Admin
describe command('python /usr/local/bin/networks_regex_tool.py /etc/httpd/apache.conf "(\"\/Auth\/Admin\">\s+Require ip\s+)((\d+\.\d+\.\d+\.\d+(\/\d+)?\s)+)" 1') do
  its('exit_status') { should eq 0 }
  its('stdout') { should eq '178.73.2.66 193.240.208.228 193.240.208.228 193.240.210.36 194.140.251.100 4.35.201.72/29 63.33.36.59 77.73.157.0/29 78.11.22.210 54.194.5.158 54.194.13.99 18.206.129.76 3.208.103.28 35.153.87.88 54.171.101.9 34.246.237.239 34.252.181.109' }
end

# Check the permitted IPs for /CallCentre/admin
describe command('python /usr/local/bin/networks_regex_tool.py /etc/httpd/apache.conf "(\"\/CallCentre\/Admin\">\s+Require ip\s+)((\d+\.\d+\.\d+\.\d+(\/\d+)?\s)+)" 1') do
  its('exit_status') { should eq 0 }
  its('stdout') { should eq '178.73.2.66 193.240.208.228 193.240.208.228 193.240.210.36 194.140.251.100 4.35.201.72/29 63.33.36.59 77.73.157.0/29 78.11.22.210 54.194.5.158 54.194.13.99 18.206.129.76 3.208.103.28 35.153.87.88 54.171.101.9 34.246.237.239 34.252.181.109' }
end
