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
from resource_management.core.system import System
import os

config = Script.get_config()

user_group = config['configurations']['cluster-env']["user_group"]
ganglia_conf_dir = default("/configurations/ganglia-env/ganglia_conf_dir", "/etc/ganglia")
ganglia_dir = "/etc/ganglia"
ganglia_runtime_dir = config['configurations']['ganglia-env']["ganglia_runtime_dir"]
ganglia_shell_cmds_dir = "/usr/libexec/hdp/ganglia"

gmetad_user = config['configurations']['ganglia-env']["gmetad_user"]
gmond_user = config['configurations']['ganglia-env']["gmond_user"]

gmond_add_clusters_str = default("/configurations/ganglia-env/additional_clusters", None)
if gmond_add_clusters_str and gmond_add_clusters_str.isspace():
  gmond_add_clusters_str = None

gmond_app_strs = [] if gmond_add_clusters_str is None else gmond_add_clusters_str.split(',')
gmond_apps = []

for x in gmond_app_strs:
  a,b = x.strip().split(':')
  gmond_apps.append((a.strip(),b.strip()))

if System.get_instance().os_family == "ubuntu":
  gmond_service_name = "ganglia-monitor"
  modules_dir = "/usr/lib/ganglia"
else:
  gmond_service_name = "gmond"
  modules_dir = "/usr/lib64/ganglia"

webserver_group = "apache"
rrdcached_base_dir = config['configurations']['ganglia-env']["rrdcached_base_dir"]
rrdcached_timeout = default("/configurations/ganglia-env/rrdcached_timeout", 3600)
rrdcached_flush_timeout = default("/configurations/ganglia-env/rrdcached_flush_timeout", 7200)
rrdcached_delay = default("/configurations/ganglia-env/rrdcached_delay", 1800)
rrdcached_write_threads = default("/configurations/ganglia-env/rrdcached_write_threads", 4)

ganglia_server_host = config["clusterHostInfo"]["ganglia_server_host"][0]

hostname = config["hostname"]
namenode_host = set(default("/clusterHostInfo/namenode_host", []))
jtnode_host = set(default("/clusterHostInfo/jtnode_host", []))
rm_host = set(default("/clusterHostInfo/rm_host", []))
hs_host = set(default("/clusterHostInfo/hs_host", []))
hbase_master_hosts = set(default("/clusterHostInfo/hbase_master_hosts", []))
datanodes_hosts = set(default("/clusterHostInfo/slave_hosts", []))
tt_hosts = set(default("/clusterHostInfo/mapred_tt_hosts", []))
nm_hosts = set(default("/clusterHostInfo/nm_hosts", []))
hbase_rs_hosts = set(default("/clusterHostInfo/hbase_rs_hosts", []))
flume_hosts = set(default("/clusterHostInfo/flume_hosts", []))
jn_hosts = set(default("/clusterHostInfo/journalnode_hosts", []))
nimbus_server_hosts = set(default("/clusterHostInfo/nimbus_hosts", []))
supervisor_server_hosts = set(default("/clusterHostInfo/supervisor_hosts", []))
kafka_broker_hosts =  set(default("/clusterHostInfo/kafka_broker_hosts", []))
kafka_ganglia_port = default("/configurations/kafka-broker/kafka.ganglia.metrics.port", 8671)

pure_slave = not hostname in (namenode_host | jtnode_host | rm_host | hs_host | \
                              hbase_master_hosts | datanodes_hosts | tt_hosts | hbase_rs_hosts | \
                              flume_hosts | nm_hosts | jn_hosts | nimbus_server_hosts | \
                              supervisor_server_hosts)
is_ganglia_server_host = (hostname == ganglia_server_host)

has_namenodes = not len(namenode_host) == 0
has_jobtracker = not len(jtnode_host) == 0
has_resourcemanager = not len(rm_host) == 0
has_historyserver = not len(hs_host) == 0
has_hbase_masters = not len(hbase_master_hosts) == 0
has_datanodes = not len(datanodes_hosts) == 0
has_tasktracker = not len(tt_hosts) == 0
has_nodemanager = not len(nm_hosts) == 0
has_hbase_rs = not len(hbase_rs_hosts) == 0
has_flume = not len(flume_hosts) == 0
has_journalnode = not len(jn_hosts) == 0
has_nimbus_server = not len(nimbus_server_hosts) == 0
has_supervisor_server = not len(supervisor_server_hosts) == 0
has_kafka_broker = not len(kafka_broker_hosts) == 0

clusters=["Slaves"]
if has_namenodes:
  clusters.append("NameNode")
if has_hbase_masters:
  clusters.append("HBaseMaster")
if has_resourcemanager:
  clusters.append("ResourceManager")
if has_nodemanager:
  clusters.append("NodeManager")
if has_historyserver:
  clusters.append("HistoryServer")
if has_datanodes:
  clusters.append("DataNode")
if has_hbase_rs:
  clusters.append("HBaseRegionServer")
if has_nimbus_server:
  clusters.append("Nimbus")
if has_supervisor_server:
  clusters.append("Supervisor")
if has_kafka_broker:
  clusters.append("Kafka")
if has_flume:
  clusters.append("FlumeServer")
if has_journalnode:
  clusters.append("JournalNode")

exclude_packages = []
if not is_ganglia_server_host:
  exclude_packages += [ "python-rrdtool", "ganglia", 
    "ganglia-devel", "ganglia-gmetad", 
    "ganglia-web", "httpd" ]

ganglia_cluster_names = {
  "jn_hosts": [("JournalNode", 8654)],
  "flume_hosts": [("FlumeServer", 8655)],
  "hbase_rs_hosts": [("HBaseRegionServer", 8656)],
  "nm_hosts": [("NodeManager", 8657)],
  "slave_hosts": [("DataNode", 8658)],
  "namenode_host": [("NameNode", 8659)],
  "hbase_master_hosts": [("HBaseMaster", 8660)],
  "rm_host": [("ResourceManager", 8661)],
  "hs_host": [("HistoryServer", 8662)],
  "nimbus_hosts": [("Nimbus", 8663)],
  "supervisor_hosts": [("Supervisor", 8664)],
  "kafka_broker_hosts": [("Kafka", kafka_ganglia_port)],
  "ReservedPort1": [("ReservedPort1", 8667)],
  "ReservedPort2": [("ReservedPort2", 8668)],
  "ReservedPort3": [("ReservedPort3", 8669)]
}

ganglia_clusters = [("Slaves", 8653)]

for key in ganglia_cluster_names:
  property_name = format("/clusterHostInfo/{key}")
  hosts = set(default(property_name, []))
  if not len(hosts) == 0:
    for x in ganglia_cluster_names[key]:
      ganglia_clusters.append(x)

if len(gmond_apps) > 0:
  for gmond_app in gmond_apps:
    ganglia_clusters.append(gmond_app)

ganglia_apache_config_file = "/etc/apache2/conf.d/ganglia.conf"
ganglia_web_path="/var/www/html/ganglia"
if System.get_instance().os_family == "suse":
  rrd_py_path = '/srv/www/cgi-bin'
  dwoo_path = '/var/lib/ganglia-web/dwoo'
  web_user = "wwwrun"
  # for upgrade purposes as path to ganglia was changed
  if not os.path.exists(ganglia_web_path):
    ganglia_web_path='/srv/www/htdocs/ganglia'

elif  System.get_instance().os_family == "redhat":
  rrd_py_path = '/var/www/cgi-bin'
  web_user = "apache"
elif  System.get_instance().os_family == "ubuntu":
  rrd_py_path = '/usr/lib/cgi-bin'
  ganglia_web_path = '/usr/share/ganglia-webfrontend'
  web_user = "www-data"
