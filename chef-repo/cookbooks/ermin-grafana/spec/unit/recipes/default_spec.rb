#
# Cookbook:: ermin-grafana
# Spec:: default
#
# Copyright:: 2020, The Authors, All Rights Reserved.
# See nvm_opsview

# Run from the cookbook directory (project root) using :
# $ cd cookbooks/ermin-grafana
# $ chef exec rspec

require 'spec_helper'

describe 'ermin-grafana::default' do
  let(:chef_instance) { ChefSpec::SoloRunner.new(platform: 'centos', version: '7') }
  let(:chef_run) { chef_instance.converge(described_recipe) }

  it 'installs grafana' do
    expect(chef_run).to install_package('grafana')
  end
end
