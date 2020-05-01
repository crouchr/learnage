title 'basic_packages'

control "joe_package" do

  title "Joe editor"
  desc "The joe editor should be installed"

  describe package('joe') do
     it { should be_installed}
  end
end
