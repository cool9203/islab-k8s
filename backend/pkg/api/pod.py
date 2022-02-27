import logging

logger = logging.getLogger(__name__)

from pkg.api import util
from flask import Flask, jsonify
from flask.views import MethodView
import pkg.kubeapi
import pkg.management

kubeapi = pkg.kubeapi._kubeapi()
manager = pkg.management._manager()


class gpu(MethodView):
    def post(self, method):
        try:
            data = util.get_request_data()
            name = data["name".upper()]
            token = data["token".upper()]
            node_name = kubeapi.get_all_pod(name)["node_name"]

            if (method == "ADD"):
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
            gpu_status = manager.get(name)["gpu_status"]

            if (method == "GET"):
                pass
            elif (method == "CREATE"):
                kubeapi._apply_svc_pv_pvc(name)
                kubeapi._apply_pod(name)
                dbapi.register(name, name, "i913")
            elif (method == "DELETE"):
                if (gpu_status in ["START", "WAIT"]):
                    manager.remove(name)
                kubeapi._delete_pod(name)
                dbapi.uid_remove(name)
            elif (method == "RESTART"):
                if (gpu_status in ["START", "WAIT"]):
                    manager.remove(name)
                kubeapi._delete_pod(name)
                kubeapi._apply_pod(name)
        except Exception as e:
            logger.error(e)
            return jsonify({"status":"unsuccess"})

def add_url_rule(app):
    api = gpu.as_view(f'gpu')
    app.add_url_rule(f'/gpu/<method>', view_func=api, methods=["POST"])

    api = pod.as_view(f'pod')
    app.add_url_rule(f'/pod/<method>', view_func=api, methods=["POST"])
