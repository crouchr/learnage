# richard

# Test the regex tool can run OK
describe command('python /usr/local/bin/networks_regex_tool.py') do
  its('exit_status') { should eq 4 }
  its('stdout') { should eq "usage : networks_regex_tool.py <filename> <regex> <capture_group_index>\n" }
end


