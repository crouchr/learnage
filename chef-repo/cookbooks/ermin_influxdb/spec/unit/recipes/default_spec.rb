#
# Cookbook:: ermin-influxdb
# Spec:: default
#
# Copyright:: 2020, The Authors, All Rights Reserved.

require 'spec_helper'

describe 'ermin-influxdb::default' do
  let (:chef_instance) { ChefSpec::SoloRunner.new(platform: 'centos', version: '7') }
  let (:chef_run) { chef_instance.converge(described_recipe) }

  it 'installs influxdb' do
    expect(chef_run).to install_package('influxdb')
  end
end
