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

describe 'ermin-mariadb::default' do
  let(:chef_instance) { ChefSpec::SoloRunner.new(platform: 'centos', version: '7') }
  let(:chef_run) { chef_instance.converge(described_recipe) }

  it 'installs mariadb-server' do
    expect(chef_run).to install_package('grafana')
  end

  it 'installs mariadb-libs' do
    expect(chef_run).to install_package('mariadb-libs')
  end

  it 'installs mariadb-devel' do
    expect(chef_run).to install_package('mariadb-devel')
  end

  it 'installs mariadb-connector-c' do
    expect(chef_run).to install_package('mariadb-connector-c')
  end
end
