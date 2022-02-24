import yaml
from pathlib import Path

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

class _db(object):
    def __init__(self, **kwargs):
        all_params = ["host", "port", "user", "passwd", "database"]
        local_params = locals()["kwargs"]
        params = dict()
        
        for key in all_params:
            if (not key in params):
                raise Exception(f"input arg key of '{key}' error.")
        params = local_params
        
        self.conn = connection=pymysql.connect(host=params["host"],
                                                port=params["port"],
                                                user=params["user"],
                                                password=params["passwd"],
                                                database=params["database"],
                                                cursorclass=pymysql.cursors.DictCursor)
        conn_status = False
        with conn:
            conn_status = True
        if (not conn_status):
            raise Exception("db connection failed")

    def command(self, sql):
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
            conn.commit()

    def select(self, sql):
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
        return result

    def create_table(self, table_name):
        pass


class _yaml(object):
    def __init__(self):
        self.docker_image = "islab-nvidia-docker-ssh-anaconda"

    def __get_name(self, name):
        all_name = self.get_all_name()
        key = secret.get_hash(name)[:8]
        while (f"{name}{key}" in all_name):
            key = secret.get_hash(name)[:8]
        return f"{name}{key}"

    def get_name_file_path(self, name):
        all_name = self.get_all_name()
        if (name in all_name):
            return str(Path(DATA_PATH, self.save_path, name).resolve())
        else:
            logger.error(f"{name} not have")
            raise Exception(f"not have name. your name is {{{name}}}")

    def create_yaml(self, name, cpu, memory, node_name, disk_size):
        config = self.load_config(name)

        name = self.__get_name(name)

        self.create_pvc_yaml(str(Path(path)), name, disk_size)
        self.create_pv_yaml(str(Path(path)), name, disk_size, str(Path(self.pv_path, name)), node_name)
        self.create_pod_yaml(str(Path(path)), name, cpu, memory, node_name, self.docker_image)
        self.create_service_yaml(str(Path(path)), name)

        config[name] = {
            "cpu": cpu,
            "memory": memory,
            "disk_size": disk_size,
            "mount_node": node_name
        }
        self.save_config(config, name)
        logger.info(f"create pod,svc,pv,pvc yaml success")
        logger.debug(f"data : {config}")
        return name

    def create_pvc_yaml(self, file_name, name, size):
        self.load_template_and_replace(str(Path(DATA_PATH, "template-pvc.yaml")), Path(file_name, "pvc.yaml"),
            name=name,
            size=size)

    def create_pv_yaml(self, file_name, name, size, path, node_name):
        self.load_template_and_replace(str(Path(DATA_PATH, "template-pv.yaml")), Path(file_name, "pv.yaml"),
            name=name,
            size=size,
            path=path,
            node_name=node_name)

    def create_service_yaml(self, file_name, name, ip=None):
        if (ip is None):
            index = len(self.get_all_name())
            ip_num_4 = index % 255
            ip_num_3 = int(2 + index / 255) % 255
            ip_num_2 = int(100 + int(2 + index / 255) / 255) % 255
            ip_num_1 = 10
            ip = f"{ip_num_1}.{ip_num_2}.{ip_num_3}.{ip_num_4}"
        self.load_template_and_replace(str(Path(DATA_PATH, "template-svc.yaml")), Path(file_name, "svc.yaml"),
            name=name,
            ip=ip)

    def create_pod_yaml(self, file_name, name, cpu, memory, node_name, image):
        self.load_template_and_replace(str(Path(DATA_PATH, "template-pod.yaml")), Path(file_name, "pod.yaml"),
            name=name,
            cpu=cpu,
            memory=memory,
            node_name=node_name,
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
            path = Path(DATA_PATH, self.save_path, name)
            self.create_pod_yaml(str(Path(path)), name, cpu, memory, node_name, self.docker_image)
        else:
            logger.info(f"edit pod {name} failed")
            raise Exception("name not have")

    def edit_svc_yaml(self, name, ports=dict()):
        logger.info(f"edit svc {name}")
        logger.debug(f"data : {ports}")

    def remove_yaml(self, name):
        path = Path(DATA_PATH, self.save_path, name)
        for file_name in ["pod.yaml", "svc.yaml", "pv.yaml", "pvc.yaml", "config"]:
            try:
                Path(path, f"{file_name}").unlink()
            except:
                pass
        path.rmdir()
        logger.info(f"remove {name}")
