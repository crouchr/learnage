
# scripts used during debugging/development etc
cookbook_file "/opt/br2020/bin/start_honeypots.sh" do
  source "scripts/start_honeypots.sh"
  mode "0755"
end

cookbook_file "/opt/br2020/bin/run_portainer.sh" do
  source "scripts/run_portainer.sh"
  mode "0755"
end

# scripts for starting up services
cookbook_file "/opt/br2020/etc/br2020.service" do
  source "scripts/br2020.service"
  mode "0644"
end

# docker compose scripts
cookbook_file "/opt/br2020/etc/br2020.yml" do
  source "scripts/br2020.yml"
  mode "0644"
end

# misc scripts
cookbook_file "/opt/br2020/bin/rules.sh" do
  source "scripts/rules.sh"
  mode "0644"
end
