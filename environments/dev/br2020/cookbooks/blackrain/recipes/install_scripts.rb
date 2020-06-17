# eventually put user runnable scripts in /opt/br2020/bin ?

# user scripts used during debugging/development etc
cookbook_file "/home/vagrant/start_amun.sh" do
  source "scripts/start_amun.sh"
  mode "0755"
  owner 'vagrant'
  group 'vagrant'
end

cookbook_file "/home/vagrant/start_glastopf.sh" do
  source "scripts/start_glastopf.sh"
  mode "0755"
  owner 'vagrant'
  group 'vagrant'
end

cookbook_file "/home/vagrant/start_cowrie.sh" do
  source "scripts/start_cowrie.sh"
  mode "0755"
  owner 'vagrant'
  group 'vagrant'
end

cookbook_file "/home/vagrant/start_honeytrap.sh" do
  source "scripts/start_honeytrap.sh"
  mode "0755"
  owner 'vagrant'
  group 'vagrant'
end

cookbook_file "/home/vagrant/start_microlinux.sh" do
  source "scripts/start_microlinux.sh"
  mode "0755"
  owner 'vagrant'
  group 'vagrant'
end

cookbook_file "/home/vagrant/start_netflow.sh" do
  source "scripts/start_netflow.sh"
  mode "0755"
  owner 'vagrant'
  group 'vagrant'
end

cookbook_file "/home/vagrant/start_p0f2.sh" do
  source "scripts/start_p0f2.sh"
  mode "0755"
  owner 'vagrant'
  group 'vagrant'
end

# user run monitoring tools
cookbook_file "/home/vagrant/run_portainer.sh" do
  source "scripts/run_portainer.sh"
  mode "0755"
  owner 'vagrant'
  group 'vagrant'
end

# scripts for starting up services
cookbook_file "/opt/br2020/etc/br2020.service" do
  source "scripts/br2020.service"
  mode "0755"
end

# docker compose scripts
cookbook_file "/opt/br2020/etc/br2020.yml" do
  source "scripts/br2020.yml"
  mode "0755"
end

# misc scripts
cookbook_file "/opt/br2020/bin/rules.sh" do
  source "scripts/rules.sh"
  mode "0755"
end
