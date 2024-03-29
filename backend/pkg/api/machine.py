import logging

logger = logging.getLogger(__name__)

from pkg.api import util
from flask import Flask, jsonify
from flask.views import MethodView
import json
import pkg.dbapi
import pkg.kubeapi

kubeapi = pkg.kubeapi._kubeapi()
yaml_file = pkg.dbapi._yaml()

worker_name = pkg.dbapi.get_worker_name()
worker_port = pkg.dbapi.get_worker_port()

class machine(MethodView):
    def post(self, method):
        if (not method in ["GET", "CREATE", "DELETE", "EDIT"]):
            return jsonify({"status":"unsuccess"})

        try:
            data = util.get_request_data()
            name_list = yaml_file.get_all_name()
            name = data["name".upper()]

            if (method == "GET" and type(name) == list):
                all_config = dict()
                for n in name:
                    config = None
                    if (n in name_list):
                        config = yaml_file.get_yaml_context(name)
                    all_config[n] = config
                return jsonify({"status":"success", "data":all_config})

            elif (method == "GET"):
                if (name == "all"):
                    logger.debug(f"get all : {name_list}")
                    return jsonify({"status":"success", "data":{"name_list":name_list}})
                elif (name in name_list):
                    config = yaml_file.get_yaml_context(name)
                    logger.debug(f"get machine {name} : {config}")
                    logger.info(f"get machine {name}")
                    return jsonify({"status":"success", "data":config})

            elif (method == "CREATE"):
                cpu = data["cpu".upper()]
                memory = data["memory".upper()]
                node_name = data["node_name".upper()]
                disk_size = data["disk_size".upper()]
                use_anaconda = True if data.get("use_anaconda", "true").lower() == "true" else False
                name = yaml_file.create_yaml(name, cpu, memory, node_name, disk_size, use_anaconda)

                worker_ip = kubeapi.get_worker(worker_name, node_name)  # 先找worker來create pv path
                ret = json.loads(util.call_api(f"http://{worker_ip}:{worker_port}/pv_creater/ADD/pod_name/{name}", "GET"))
                if (ret["status"] == "success"):
                    kubeapi._apply_pv_pvc(name)
                    return jsonify({"status":"success", "name":name})
                else:
                    return jsonify({"status":"unsuccess"})

            elif (method == "DELETE"):
                #沒有實作
                return jsonify({"status":"unsuccess", "name":name})

            elif (method == "EDIT"):
                cpu = data["cpu".upper()]
                memory = data["memory".upper()]
                node_name = data["node_name".upper()]
                disk_size = data["disk_size".upper()]
                image = data.get("image", "islab-nvidia-docker-ssh-anaconda")
                name = yaml_file.edit_pod_yaml(name, cpu, memory, node_name, image)
                return jsonify({"status":"success", "name":name})

        except Exception as e:
            logger.error(e)
            return jsonify({"status":"unsuccess"})

def add_url_rule(app):
    api = machine.as_view(f'machine')
    app.add_url_rule(f'/machine/<method>', view_func=api, methods=["POST"])
