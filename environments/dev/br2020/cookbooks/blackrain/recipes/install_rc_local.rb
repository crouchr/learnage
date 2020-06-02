# Install

cookbook_file "/etc/rc.local" do
  source "rc.local"
  mode "0777"
end

