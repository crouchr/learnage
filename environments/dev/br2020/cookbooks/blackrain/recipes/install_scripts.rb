cookbook_file "/opt/br2020/bin/start_honeypots.sh" do
  source "start_honeypots.sh"
  mode "0755"
end

cookbook_file "/opt/br2020/bin/rules.sh" do
  source "rules.sh"
  mode "0644"
end

cookbook_file "/opt/br2020/etc/br2020.service" do
  source "br2020.service"
  mode "0644"
end

cookbook_file "/opt/br2020/etc/br2020.yml" do
  source "br2020.yml"
  mode "0644"
end