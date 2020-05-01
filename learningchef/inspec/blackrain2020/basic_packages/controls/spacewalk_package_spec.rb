title 'basic_packages'

control "spacewalk_package" do

  title "Spacewalk"
  desc "Spacewalk package(s) should be installed"

  describe package('spacewalk-client-repo') do
     it { should be_installed}
  end

  describe package('spacewalk-usix') do
     it { should be_installed}
  end

end
