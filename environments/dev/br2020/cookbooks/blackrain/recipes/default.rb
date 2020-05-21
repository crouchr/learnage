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
# NOTE - STILL A WORK IN PROGRESS
#
# NOTES : Just a dummy to test it does something
#

execute 'install_snort' do
  command 'yum -y install http://web.ermin/br2020-packages/snort-2.9.16-1.centos7.x86_64.rpm'
  user 'root'
end

package 'prelude-manager-db-plugin'
package 'prelude-lml'
package 'prelude-lml-rules'
package 'prelude-correlator'
# fails : package 'python3-prewikka'
package 'prelude-tools'
package 'preludedb-tools'
package 'preludedb-mysql'
