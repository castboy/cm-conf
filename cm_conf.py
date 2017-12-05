import strictyaml
from cm_api.api_client import ApiResource

conf_yml= "conf.yml"


def yml_string(file):
    file_object = open(file)
    try:
         s = file_object.read( )
    finally:
         file_object.close( )
    return s



def yml_direct(s):
    return strictyaml.load(s).data



def api(host, user, passwd, version):
    return ApiResource(server_host=host, username=user, password=passwd, version=version)


def cdh(api):
    return api.get_cluster("cluster")


def services(cdh):
    direct = {}
    for s in cdh.get_all_services():
        if s.type == "HDFS":
            direct["service_hdfs"] = s
        elif s.type == "KAFKA":
            direct["service_kafka"] = s
        elif s.type == "YARN":
            direct["service_yarn"] = s
        else:
            direct["service_zookeeper"] = s
    return direct


def services_restart(direct):
    for key in direct:
        direct[key].restart()



def conf_hdfs(service_hdfs, conf_hdfs):
    service_hdfs.update_config(conf_hdfs["service"])
    
    group_namenode = service_hdfs.get_role_config_group("{0}-NAMENODE-BASE".format("hdfs"))
    group_namenode.update_config(conf_hdfs["namenode"])

    group_datanode = service_hdfs.get_role_config_group("{0}-DATANODE-BASE".format("hdfs"))
    group_datanode.update_config(conf_hdfs["datanode"])

    group_gateway = service_hdfs.get_role_config_group("{0}-GATEWAY-BASE".format("hdfs"))
    group_gateway.update_config(conf_hdfs["gateway"])



def conf_kafka(service_kafka, conf_kafka):
    service_kafka.update_config(conf_kafka["service"])

    group_broker = service_kafka.get_role_config_group("{0}-KAFKA_BROKER-BASE".format("kafka"))
    group_broker.update_config(conf_kafka["kafka_broker"])


def conf_yarn(service_yarn, conf_yarn):
    group_rm = service_yarn.get_role_config_group("{0}-RESOURCEMANAGER-BASE".format("yarn"))
    group_rm.update_config(conf_yarn["resource_manager"])

    group_nm = service_yarn.get_role_config_group("{0}-NODEMANAGER-BASE".format("yarn"))
    group_nm.update_config(conf_yarn["node_manager"])
    
def main():
    conf = yml_string(conf_yml)
    d = yml_direct(conf)
    a= api(d["cluster"]["cm_host"], d["cluster"]["username"], d["cluster"]["password"], d["cluster"]["api_version"])
    c = cdh(a)
    s = services(c)
    conf_hdfs(s["service_hdfs"], d["hdfs"])
    conf_kafka(s["service_kafka"], d["kafka"])
    conf_yarn(s["service_yarn"], d["yarn"])
    

    services_restart(s)




if __name__=="__main__":
    main()
