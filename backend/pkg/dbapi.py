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
