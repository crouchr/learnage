control "world-1" do                                  # A unique ID for this control
  impact 1.0                                          # Just how critical is
  title "Joe editor"                                  # Readable by a human
  desc "The joe editor should be installed"           # Optional description
  describe package('joe8') do                          # The actual test
     it { should be_installed}
  end
end
