cookbook_file "/app/scripts/start_honeypots.sh" do
  source "start_honeypots.sh"
  mode "0755"
end

cookbook_file "/app/scripts/br2020-compose.yml" do
  source "br2020-compose.yml"
  mode "0644"
end
