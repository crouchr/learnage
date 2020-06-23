require 'chefspec'

at_exit { ChefSpec::Coverage.report! }

describe 'blackrain::install_dev_tools' do
  let(:chef_run) {
    ChefSpec::Runner.new.converge('blackrain::install_dev_tools')
  }

  it 'installs gcc' do
    expect(chef_run).to install_package('gcc')
  end

  it 'installs git' do
    expect(chef_run).to install_package('git')
  end

end
