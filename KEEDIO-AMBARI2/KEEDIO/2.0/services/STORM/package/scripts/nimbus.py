#!/usr/bin/env python
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

"""

from resource_management import *
from storm import storm


class Nimbus(Script):
  def install(self, env):
    import params
    self.install_packages(env)
    Package("storm-nimbus")
    self.configure(env)

  def configure(self, env):
    import params
    env.set_params(params)
    File('/etc/monit.d/storm-nimbus',content=StaticFile('monit.d_storm-nimbus'))
    if params.has_ganglia_server:
       File('/var/lib/jmxtrans/nimbus.json',
          content=Template('nimbus.json.j2')
       )
       File('/var/lib/jmxtrans/nimbusjvm.json',
          content=Template('nimbusjvm.json.j2')
       )
    storm(action="config")

  def start(self, env):
    import params
    env.set_params(params)
    self.configure(env)

    storm(service="storm-nimbus", action="start")
    storm(service="jmxtrans", action="start")

  def stop(self, env):
    import params
    env.set_params(params)

    storm(service="storm-nimbus", action="stop")
    storm(service="jmxtrans", action="stop")

  def status(self, env):
    import status_params
    env.set_params(status_params)

    storm(service="storm-nimbus", action="status")

if __name__ == "__main__":
  Nimbus().execute()
