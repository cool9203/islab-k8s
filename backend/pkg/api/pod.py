import logging

logger = logging.getLogger(__name__)

from pkg.api import util
from flask import Flask, jsonify
from flask.views import MethodView
import time
import json
import pkg.kubeapi
import pkg.dbapi
import pkg.management

kubeapi = pkg.kubeapi._kubeapi()
yaml_file = pkg.dbapi._yaml()
manager = pkg.management._manager()
manager.start()


class gpu(MethodView):
    def post(self, method):
        if (not method in ["SADD", "ADD", "REMOVE", "GET"]):
            return jsonify({"status":"unsuccess"})

        try:
            data = util.get_request_data()
            name = data["name".upper()]
            token = data["token".upper()]
            node_name = kubeapi.get_all_pod(name)[name]["node_name"]

            if (method == "SADD"):
                if (token == "islabs102a"):
                    weeks = data["weeks"]
                    days = data["days"]
                    hours = data["hours"]
                    minutes = data["minutes"]
                    seconds = data["seconds"]
                    delta_time = {"weeks":weeks, "days":days, "hours":hours , "minutes":minutes, "seconds":seconds}
                    if (manager.add(node_name, name, delta_time)):
                        return jsonify({"status":"success"})
            elif (method == "ADD"):
                if (manager.add(node_name, name)):
                    return jsonify({"status":"success"})
            elif(method == "REMOVE"):
                if (manager.remove(node_name, name)):
                    return jsonify({"status":"success"})
            elif(method == "GET"):
                response_data = manager.get(node_name, name)
                response_data["status"] = "success"
                return jsonify(response_data)
            return jsonify({"status":"unsuccess"})

        except Exception as e:
            logger.error(e)
            return jsonify({"status":"unsuccess"})


class pod(MethodView):
    def post(self, method):
        if (not method in ["GET", "CREATE", "DELETE", "RESTART"]):
            return jsonify({"status":"unsuccess"})

        try:
            data = util.get_request_data()
            name = data["name".upper()]
            token = data["token".upper()]
            node_name = yaml_file.get_yaml_context(name)["node_name"]
            gpu_status = manager.get(node_name, name)["gpu_status"]

            if (method == "GET"):
                ret = kubeapi.get_all_pod(name)
                if (len(ret) > 0):
                    ip = list(kubeapi.get_all_svc(name).keys())[0]
                    status = str(ret[0]["status"])
                    return jsonify({"status":"success", "pod_status":status, "ip":ip})
                else:
                    return jsonify({"status":"success", "pod_status":"noready"})
            elif (method == "CREATE"):
                kubeapi._delete_svc(name)           # 因為有設定clusterIP，所以會引發重複設定的error，所以需要先delete，後apply
                kubeapi._apply_svc(name)
                kubeapi._apply_pod(name)
                pkg.dbapi.register(name, "i913", name)
            elif (method == "DELETE"):
                if (gpu_status in ["START", "WAIT"]):
                    manager.remove(node_name, name)
                kubeapi._delete_pod(name)
                kubeapi._delete_svc(name)
                pkg.dbapi.uid_remove(name)
            elif (method == "RESTART"):
                if (gpu_status in ["START", "WAIT"]):
                    manager.remove(node_name, name)
                kubeapi._delete_pod(name)
                time.sleep(3)
                kubeapi._apply_pod(name)
            return jsonify({"status":"success"})
        except Exception as e:
            logger.error(e)
            return jsonify({"status":"unsuccess"})

def add_url_rule(app):
    api = gpu.as_view(f'gpu')
    app.add_url_rule(f'/gpu/<method>', view_func=api, methods=["POST"])

    api = pod.as_view(f'pod')
    app.add_url_rule(f'/pod/<method>', view_func=api, methods=["POST"])
