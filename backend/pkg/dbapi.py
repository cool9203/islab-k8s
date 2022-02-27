import logging

logger = logging.getLogger(__name__)

import yaml
from pathlib import Path
import pymysql.cursors
import pkg.kubeapi
import pkg.secret
import ipaddress
import re


def get_worker_name():
    with Path("./deploy/worker.yaml").open("r") as f:
        worker_yaml = yaml.load(f, Loader=yaml.FullLoader)
        worker_name = worker_yaml["metadata"]["name"]
    return worker_name


def get_worker_port():
    with Path("./deploy/worker.yaml").open("r") as f:
        worker_yaml = yaml.load(f, Loader=yaml.FullLoader)
        worker_port = worker_yaml["spec"]["template"]["spec"]["containers"][0]["ports"][0]["containerPort"]
    return worker_port


def __get_action_last_uid():
    ret = db.select("select count(*) from log")
    return ret[0]["count(*)"]


def add_log(config):
    try:
        action_uid = __get_action_last_uid()
        name = config["name"]
        status = config["status"]
        start_time = config.get("start_time", "")
        end_time = config.get("end_time", "")
        db.command(f"INSERT INTO log VALUES ('{action_uid}', '{name}', '{status}', '{start_time}', '{end_time}')")
        return True
    except Exception as e:
        return False


def uid_remove(uid):
    try:
        db.command(f"DELETE FROM account WHERE `uid` = '{uid}' AND `permission` != 0")
        return True
    except Exception as e:
        return False


def login(uid, password):
    try:
        ret = db.select(f"SELECT * FROM account WHERE `uid` = '{uid}'")
        if (len(ret) == 0):
            raise Exception("uid error")
        if (password == ret[0]["password"]):
            return ret[0]
        else:
            raise Exception("password error")
    except Exception as e:
        raise Exception("error")


def register(uid, password, name):
    try:
        db.command(f"INSERT INTO account VALUES ('{uid}', '{password}', '{name}', 4)")
        return True
    except Exception as e:
        return False


class _db(object):
    def __init__(self, **kwargs):
        all_params = ["host", "port", "user", "password", "database"]
        local_params = locals()["kwargs"]
        params = dict()
        
        for key in local_params.keys():
            if (not key in all_params):
                raise Exception(f"input arg key of '{key}' error.")
        params = local_params
        
        self.host = params["host"]
        self.port = params["port"]
        self.user = params["user"]
        self.password = params["password"]
        self.database = params["database"]

        self.connect()

    def connect(self):
        self.conn = connection=pymysql.connect(host=self.host,
                                                port=self.port,
                                                user=self.user,
                                                password=self.password,
                                                database=self.database,
                                                cursorclass=pymysql.cursors.DictCursor)

    def is_connect(self):
        try:
            self.conn.ping(reconnect=True)
        except:
            self.connect()

    def command(self, sql):
        self.is_connect()
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
        self.conn.commit()
        self.conn.close()

    def select(self, sql):
        self.is_connect()
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        self.conn.close()
        return result


class _yaml(object):
    def __init__(self):
        self.default_docker_image = {"anaconda":"islab-nvidia-docker-ssh-anaconda", "base":"islab-nvidia-docker-ssh"}
        self.pv_path = "/mnt/k8s-data"

    def __get_name(self, name):
        all_name = self.get_all_name()
        print(all_name)
        key = pkg.secret.get_hash(name)[:8]
        while (f"{name}{key}" in all_name):
            key = secret.get_hash(name)[:8]
        return f"{name}{key}"

    def get_all_name(self):
        name_list = list()
        for element in Path("./data/yaml").iterdir():
            name_list.append(element.name)
        return name_list

    def get_yaml_context(self, name):
        data = dict()

        with Path("./data/yaml", name, "pod.yaml").open("r") as f:
            pod_data = yaml.load(f, Loader=yaml.FullLoader)
            data["cpu"] = pod_data["spec"]["containers"][0]["resources"]["requests"]["cpu"]
            data["memory"] = pod_data["spec"]["containers"][0]["resources"]["requests"]["memory"]

        with Path("./data/yaml", name, "pv.yaml").open("r") as f:
            pv_data = yaml.load(f, Loader=yaml.FullLoader)
            data["disk_size"] = pv_data["spec"]["capacity"]["storage"]
            data["node_name"] = pv_data["spec"]["nodeAffinity"]["required"]["nodeSelectorTerms"][0]["matchExpressions"][0]["values"][0]

        return data

    def __get_all_yaml_ip(self):
        all_ip = list()
        path = Path(f"./data/yaml")
        for dir_name in path.iterdir():
            try:
                with Path(path, dir_name.name, "svc.yaml").open("r") as f:
                    svc_data = yaml.load(f, Loader=yaml.FullLoader)
                    all_ip.append(svc_data["spec"]["clusterIP"])
            except Exception as e:
                pass
        return all_ip

    def __get_idle_ip(self, start_ip="10.100.0.0"):
        all_ip = list(kubeapi.get_all_svc().keys()) + self.__get_all_yaml_ip()
        logger.info(f"all_ip:{all_ip}")
        ipa = ipaddress.ip_address(start_ip)
        ipn = ipaddress.ip_network(f"{start_ip}/16")
        for ip in ipn.hosts():
            if (not str(ip) in all_ip):
                return str(ip)
        return self.__get_idle_ip(str(ipa + ipn.num_addresses))

    def create_yaml(self, name, cpu, memory, node_name, disk_size, use_anaconda):
        name = self.__get_name(name)
        image = self.default_docker_image["anaconda"] if use_anaconda is True else self.default_docker_image["base"]

        #this path is cp only use, so can create.
        path = Path(f"./data/yaml/{name}")
        path.mkdir(exist_ok=True)

        self.create_pvc_yaml(path, name, disk_size)
        self.create_pv_yaml(path, name, disk_size, str(Path(self.pv_path, name)), node_name)
        self.create_pod_yaml(path, name, cpu, memory, image)
        self.create_service_yaml(path, name)
        return name

    def create_pvc_yaml(self, file_name, name, size):
        self.load_template_and_replace(Path("./data", "template-pvc.yaml"), Path(file_name, "pvc.yaml"),
            name=name,
            size=size)

    def create_pv_yaml(self, file_name, name, size, path, node_name):
        self.load_template_and_replace(Path("./data", "template-pv.yaml"), Path(file_name, "pv.yaml"),
            name=name,
            size=size,
            path=path,
            node_name=node_name)

    def create_service_yaml(self, file_name, name):
        ip = self.__get_idle_ip()
        self.load_template_and_replace(Path("./data", "template-svc.yaml"), Path(file_name, "svc.yaml"),
            name=name,
            ip=ip)

    def create_pod_yaml(self, file_name, name, cpu, memory, image):
        self.load_template_and_replace(Path("./data", "template-pod.yaml"), Path(file_name, "pod.yaml"),
            name=name,
            cpu=cpu,
            memory=memory,
            image=image)

    def load_template_and_replace(self, template_name, save_path, **kwargs):
        with Path(template_name).open("r", encoding="utf8") as template_file:
            template = template_file.read()
            
            for key, value in kwargs.items():
                template = template.replace(f"{{{key}}}", str(value))
            
            res = re.search(r"{\w*}", template)
            if (not res is None):
                raise Exception(f"{template_name} have not replace patten:{res.group(0)}")

        with Path(save_path).open("w", encoding="utf8") as f:
            f.write(template)

    def edit_pod_yaml(self, name, cpu, memory, node_name, image):
        all_name = self.get_all_name()
        if (name in all_name):
            logger.info(f"edit pod {name} success")
            logger.debug(f"data : cpu:{cpu}, memory:{memory}, node_name:{node_name}, image:{image}")
            path = Path(f"./data/yaml/{name}")
            self.create_pod_yaml(path, name, cpu, memory, node_name, image)
        else:
            logger.info(f"edit pod {name} failed")
            raise Exception("name not have")

    def remove_yaml(self, name):
        path = Path(DATA_PATH, self.save_path, name)
        for file_name in ["pod.yaml", "svc.yaml", "pv.yaml", "pvc.yaml", "config"]:
            try:
                Path(path, f"{file_name}").unlink()
            except:
                pass
        path.rmdir()
        logger.info(f"remove {name}")


kubeapi = pkg.kubeapi._kubeapi()
db_info = kubeapi.get_all_pod("islab-db")
db = _db(host=db_info["islab-db"]["pod_ip"], port=3306, user="root", password="password", database="test")
