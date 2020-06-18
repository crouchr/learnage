title 'containers'

control "amun_container" do

  title "Amun Container"
  desc "Amun container should be installed"

  describe docker_container(name: 'amun') do
    it { should exist }
    it { should be_running }
   end

end
