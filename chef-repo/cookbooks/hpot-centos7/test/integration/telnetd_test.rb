describe package 'telnet-server' do
  it { should be_installed }
end

describe service 'telnet.socket' do
  it { should be_enabled }
  it { should be_running }
end

describe port 23 do
  it { should be_listening }
end
