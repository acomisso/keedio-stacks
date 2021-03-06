"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Ambari Agent

"""
from resource_management import *
from resource_management.libraries.functions.dynamic_variable_interpretation import copy_tarballs_to_hdfs

from mapreduce_historyserver import historyserver

class HistoryServer(Script):
  def install(self, env):
    import params

    self.install_packages(env,params.exclude_packages)
    env.set_params(params)
    #historyserver(action="configure")

  def start(self, env):
    import params

    env.set_params(params)
    historyserver(action="configure")
    # copy_tarballs_to_hdfs('mapreduce', params.mapred_user, params.hdfs_user, params.user_group)
    historyserver(action="start")

  def stop(self, env):
    import params

    env.set_params(params)
    historyserver(action="stop")

  def status(self, env):
    import status_params

    env.set_params(status_params)
    historyserver(action="status")

if __name__ == "__main__":
  HistoryServer().execute()
