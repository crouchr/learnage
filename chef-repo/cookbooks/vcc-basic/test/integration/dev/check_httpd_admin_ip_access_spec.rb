
# Check the permitted IPs for /Auth/Admin
#describe command('python /usr/local/bin/networks_regex_tool.py /etc/httpd/apache.conf "(\/Auth\/Admin>\s+Require ip\s+)((\d+\.\d+\.\d+\.\d+(\/\d+)?\s)+)" 1') do
#  its('exit_status') { should eq 0 }
#  its('stdout') { should eq '127.0.0.1 172.16.1.0/24 172.17.1.1' }
#end

# Check the permitted IPs for /CallCentre/Admin
describe command('python /usr/local/bin/networks_regex_tool.py /etc/httpd/apache.conf "(\/CallCentre\/Admin>\s+Require ip\s+)((\d+\.\d+\.\d+\.\d+(\/\d+)?\s)+)" 1') do
  its('exit_status') { should eq 0 }
  its('stdout') { should eq '127.0.0.1 172.16.1.0/24 172.17.1.1' }
end
