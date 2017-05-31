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
from subprocess import *

def gmetad(action=None):
  # 'start' or 'stop'
  cmd=Popen(['service','gmetad',action],stdout=PIPE,stderr=PIPE)
  out,err=cmd.communicate()
  rc=cmd.returncode
  Logger.info("Ganglia gmetad service %s: %s" % (action, cmd.returncode == 0))
   
  if action == "status":
    from functions import check_rc
    check_rc(rc,stdout=out,stderr=err)
  if action =="start" or action == "stop":
   # MonitorWebserver("restart") Not compatible with centos 7
     cmd=Popen(['service','httpd',action],stdout=PIPE,stderr=PIPE)
     out,err=cmd.communicate()
     rc=cmd.returncode
     Logger.info("Httpd service %s: %s" % (action, cmd.returncode == 0))
