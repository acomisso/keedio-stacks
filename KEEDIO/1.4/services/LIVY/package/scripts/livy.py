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
import os

from resource_management import *
from subprocess import *
from utils import check_rc
def livy(action=None):
  
  if action == 'start' or action == 'stop' or action == 'status':
    cmd=Popen(['service','livy',action],stdout=PIPE,stderr=PIPE)
    out,err=cmd.communicate()
    Logger.info('Zeppelin action: %s.\nSTDOUT=%s\nSTDERR=%s' % (action,out,err))
    if action == 'start' or action == 'status':
      check_rc(cmd.returncode,stdout=out,stderr=err)

  if action == 'config' :
    import params
    File('/etc/livy/conf/spark-blacklist.conf',
      content=Template('spark-blacklist.conf.j2'),
      owner='livy',
      group='livy',
      mode=0550
    )
    File('/etc/livy/conf/livy-env.sh',
      content=Template('livy-env.sh.j2'),
      owner='livy',
      group='livy',
      mode=0550
    )
    File('/etc/livy/conf/livy.conf',
      content=Template('livy.conf.j2'),
      owner='livy',
      group='livy',
      mode=0550
    )
