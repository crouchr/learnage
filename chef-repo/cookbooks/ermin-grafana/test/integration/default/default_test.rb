# InSpec test for recipe ermin-grafana::default

# The InSpec reference, with examples and extensive documentation, can be
# found at https://www.inspec.io/docs/reference/resources/

describe package('grafana') do
  it { should be_installed }
end
