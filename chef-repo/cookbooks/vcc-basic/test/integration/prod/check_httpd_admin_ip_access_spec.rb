
# Check the permitted IPs for /Auth/Admin
describe command('python /usr/local/bin/networks_regex_tool.py /etc/httpd/apache.conf "(\"\/Auth\/Admin\">\s+Require ip\s+)((\d+\.\d+\.\d+\.\d+(\/\d+)?\s)+)" 1') do
  its('exit_status') { should eq 0 }
  its('stdout') { should eq '1.1.1.1 2.2.2.2' }
end

# Check the permitted IPs for /CallCentre/admin
describe command('python /usr/local/bin/networks_regex_tool.py /etc/httpd/apache.conf "(\"\/CallCentre\/Admin\">\s+Require ip\s+)((\d+\.\d+\.\d+\.\d+(\/\d+)?\s)+)" 1') do
  its('exit_status') { should eq 0 }
  its('stdout') { should eq '1.1.1.1 2.2.2.2' }
end
