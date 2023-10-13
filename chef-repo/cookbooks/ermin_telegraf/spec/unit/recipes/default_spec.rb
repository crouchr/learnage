#
# Cookbook:: ermin-telegraf
# Spec:: default
#
# Copyright:: 2020, The Authors, All Rights Reserved.

require 'spec_helper'

describe 'ermin-telegraf::default' do
  let (:chef_instance) { ChefSpec::SoloRunner.new(platform: 'centos', version: '7') }
  let (:chef_run) { chef_instance.converge(described_recipe) }

  it 'installs telegraf' do
    expect(chef_run).to install_yum_package('/tmp/telegraf-1.15.3-1.x86_64.rpm')
  end
end

