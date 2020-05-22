#
# Cookbook Name:: blackrain
# Recipe:: default
# Author:: Richard Crouch (richard.crouch100@gmail.com)
#
# Copyright (C) 2020 Me, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# did not work - would allow adding fprobe as package
#yum-config-manager --add-repo https://centos.pkgs.org/7/lux/
#yum-config-manager --enable centos.pkgs.org_7_lux_








# CLAMAV
# ======
package 'clamav-server'
package 'clamav-data'
package 'clamav-update'
package 'clamav-filesystem'
package 'clamav'
package 'clamav-scanner-systemd'
package 'clamav-devel'
package 'clamav-lib'
package 'clamav-server-systemd'
log 'Installed ClamAV'




# TODO
#=====
# FROM https://centos.pkgs.org/7/lux/
# fprobe
# maldet




