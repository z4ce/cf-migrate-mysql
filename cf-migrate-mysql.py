#!/usr/bin/env python3
import subprocess
import json
import argparse

class CfCli:
  def __init__(self, instance):
    self.instance = instance
  def curl(self, url):
    return json.loads(self.cmd("curl '" + url +"'"))

  def cmd(self, command):
    print("Running cf: " + command)
    return subprocess.getoutput("CF_HOME="+ self.instance + " cf " + command).rstrip()

def main():
  parser = argparse.ArgumentParser(description="Moves MySQL from one space to another including creating services.\
                        Service plans must be the same between environments.")
  parser.add_argument("--src-api", dest="src_api",
                    help="URL for source API", required=True)
  parser.add_argument("--src-user", dest="src_user",
                    help="username for source API", required=True)
  parser.add_argument("--src-pass", dest="src_pass",
                    help="password for source API", required=True)
  parser.add_argument("--src-org", dest="src_org",
                    help="org name for source", required=True)
  parser.add_argument("--src-space", dest="src_space",
                    help="space name for source", required=True)
  parser.add_argument("--dst-api", dest="dst_api",
                    help="URL for destination API", required=True)
  parser.add_argument("--dst-user", dest="dst_user",
                    help="username for destination API", required=True)
  parser.add_argument("--dst-pass", dest="dst_pass",
                    help="password for destination API", required=True)
  parser.add_argument("--dst-org", dest="dst_org",
                    help="org name for destination", required=True)
  parser.add_argument("--dst-space", dest="dst_space",
                    help="space name for destination", required=True)

  args = parser.parse_args()
  (src, org_guid, space_guid) = build_cli("src", vars(args))
  (dst, dst_org_guid, dst_space_guid) = build_cli("dst", vars(args))

  space_obj = dst.curl("v2/spaces/" + space_guid + "/summary")
  for service in space_obj['services']:
    if service['service_plan']['service']['label'] == "p-mysql":
      process_service(service, service['service_plan'], src, dst)

def build_cli (name, options):
  dst = CfCli(name)
  dst.cmd("api --skip-ssl-validation " + options[name + "_api"])
  dst.cmd("auth " + options[name + "_user"] + " " + options[name + "_pass"])
  dst.cmd("target -o " + options[name + "_org"])
  org_guid = dst.cmd("org --guid " + options[name + "_org"])
  dst.cmd("target -s " + options[name + "_space"])
  space_guid = dst.cmd("space --guid " + options[name + "_space"])
  return (dst, org_guid, space_guid)

def process_service(service, service_plan, src, dst):
  # Get the database contents
  src.cmd("create-service-key " + service['name'] + " migration_key")
  sk_obj = src.curl("v2/service_instances/"+service['guid']+"/service_keys?q=name:migration_key")
  entity = sk_obj['resources'][0]['entity']['credentials']
  mysqldump(entity['hostname'], entity['port'], entity['username'], entity['password'], entity['name'])
  src.cmd("delete-service-key -f " + service['name'] + " migration_key")

  # Restore into new environment
  dst.cmd("create-service p-mysql " + service_plan['name'])
  dst.cmd("create-service-key " + service['name'] + " migration_key")
  dst_sk = dst.curl("v2/service_instances/"+service['guid']+"/service_keys?q=name:migration_key")
  dst_entity = sk_obj['resources'][0]['entity']['credentials']
  mysqlimport(dst_entity['hostname'], dst_entity['port'], dst_entity['username'], dst_entity['password'], dst_entity['name'], entity['name'])
  dst.cmd("delete-service-key -f " + service['name'] + " migration_key")

def mysqldump(hostname, port, username, password, db_name):
  mysql_cmd = "".join(["mysqldump --user=", username, " --password=", password, " --host=", hostname, " --port=", str(port), " ", db_name, " --single-transaction --skip-add-locks > ", "/tmp/", db_name, ".dump"])
  print(mysql_cmd)
  subprocess.getoutput(mysql_cmd)

def mysqlimport(hostname, port, username, password, db_name, old_db_name):
  mysql_cmd = "".join(["mysql --user=", username, " --password=", password, " --host=", hostname, " --port=", str(port), " ", db_name, "< ", "/tmp/", old_db_name, ".dump"])
  print(mysql_cmd)
  subprocess.getoutput(mysql_cmd)

if __name__ == '__main__':
  main()
