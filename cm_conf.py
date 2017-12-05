import strictyaml, os
from cm_api.api_client import ApiResource


conf_yml= "conf.yml"


def yml_string(file):
    try:
        file_object = open(file)
        s = file_object.read()
    except:
        print "conf.yml not found"
        os._exit(0)
    finally:
        file_object.close()

    return s



def yml_direct(s):
    try:
        d = strictyaml.load(s).data
    except:
        print "error in *.yml"
        os._exit(0)

    return d


def api(host, user, passwd, version):
    try:
        api = ApiResource(server_host=host, username=user, password=passwd, version=version)
    except:
        print "create cm-api error, check *.yml [cluster] item"
        os._exit(0)

    return api



def cdh(api):
    try:
        cdh = api.get_cluster("cluster")
    except:
        print "create cdh error"
        os._exit(0)
        
    return cdh



def services(cdh):
    try:
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
    except:
        print "get all services failed"
        os._exit(0)

    return direct



def services_restart(direct):
    try:
        for key in direct:
            direct[key].restart()
    except:
        print "services restart failed"
        os._exit(0)


def conf_hdfs(service_hdfs, conf_hdfs):
    try:
        service_hdfs.update_config(conf_hdfs["service"])
        
        group_namenode = service_hdfs.get_role_config_group("{0}-NAMENODE-BASE".format("hdfs"))
        group_namenode.update_config(conf_hdfs["namenode"])

        group_datanode = service_hdfs.get_role_config_group("{0}-DATANODE-BASE".format("hdfs"))
        group_datanode.update_config(conf_hdfs["datanode"])

        group_gateway = service_hdfs.get_role_config_group("{0}-GATEWAY-BASE".format("hdfs"))
        group_gateway.update_config(conf_hdfs["gateway"])
    except:
        print "config hdfs error, check *.yml [hdfs] config"
        os._exit(0)


def conf_kafka(service_kafka, conf_kafka):
    try:
        service_kafka.update_config(conf_kafka["service"])

        group_broker = service_kafka.get_role_config_group("{0}-KAFKA_BROKER-BASE".format("kafka"))
        group_broker.update_config(conf_kafka["kafka_broker"])
    except:
        print "config kafka error, check *.yml [kafka] config"
        os._exit(0)


def conf_yarn(service_yarn, conf_yarn):
    try:
        group_rm = service_yarn.get_role_config_group("{0}-RESOURCEMANAGER-BASE".format("yarn"))
        group_rm.update_config(conf_yarn["resource_manager"])

        group_nm = service_yarn.get_role_config_group("{0}-NODEMANAGER-BASE".format("yarn"))
        group_nm.update_config(conf_yarn["node_manager"])
    except:
        print "config yarn error, check *.yml [yarn] config"
        os._exit(0)


    
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

    print "config cm success"


if __name__=="__main__":
    main()
