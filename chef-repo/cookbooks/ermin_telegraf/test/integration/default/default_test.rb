# InSpec test for recipe ermin-telegraf::default

# The InSpec reference, with examples and extensive documentation, can be
# found at https://www.inspec.io/docs/reference/resources/

describe package('telegraf') do
  it { should be_installed }
end
