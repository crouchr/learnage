cookbook_file "/app/scripts/start_honeypots.sh" do
  source "start_honeypots.sh"
  mode "0755"
end

cookbook_file "/app/scripts/docker-compose.yml" do
  source "docker-compose.yml"
  mode "0644"
end
