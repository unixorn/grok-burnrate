#
# Copyright 2013, Numenta Inc.
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
# limitations under the License

if not ENV.has_key?('CONTAINER_NAME')
  CONTAINER_NAME="grok/burnrate"
else
  CONTAINER_NAME=ENV['CONTAINER_NAME']
end

# Load GROK_SERVER and GROK_API_KEY from environment if present
if not ENV.has_key?('GROK_SERVER')
  GROK_SERVER="https://yourEC2instance.example.com"
else
  GROK_SERVER=ENV['GROK_SERVER']
end
if not ENV.has_key?('GROK_API_KEY')
  GROK_API_KEY="abc123"
else
  GROK_API_KEY=ENV['GROK_API_KEY']
end

task :help do
  sh %{ rake -T }
end

desc "Create/Update #{CONTAINER_NAME}"
task :build do
  sh %{ docker build -t #{CONTAINER_NAME} . }
end

desc "Push #{CONTAINER_NAME}"
task :push do
  sh %{ docker push #{CONTAINER_NAME} }
end

desc "test #{CONTAINER_NAME} container"
task :test => [:build] do
  sh %{ docker run --rm -i -e GROK_SERVER="#{GROK_SERVER}" -e GROK_API_KEY="#{GROK_API_KEY}" -t #{CONTAINER_NAME}  /bin/bash }
end

desc "history of #{CONTAINER_NAME}"
task :history do
  sh %{ docker history #{CONTAINER_NAME} }
end

task :b => [:build]
task :default => [:help]
task :h => [:history]
task :t => [:test]
