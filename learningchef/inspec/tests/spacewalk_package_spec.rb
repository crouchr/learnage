control "world-2" do
  impact 1.0
  title "Spacewalk"
  desc "Spacewalk packages should be installed"

  describe package('spacewalk-client-repo') do
     it { should be_installed}
  end
  describe package('spacewalk-usix') do
     it { should be_installed}
  end

end
