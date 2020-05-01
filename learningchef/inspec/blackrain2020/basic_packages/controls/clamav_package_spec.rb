title 'clamav'

control "clamav_package_spec" do
  title "ClamAV AV"
  desc "The ClamAV AV tool should be installed"

  describe package('clamav') do
     it { should be_installed}
  end
end
