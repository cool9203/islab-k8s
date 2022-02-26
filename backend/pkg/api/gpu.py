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
            data = get_request_data()
            name = data["name".upper()]
            token = data["token".upper()]
            node_name = kubeapi.get_all_pod(name)["node_name"]

            if (type_name == "ADD"):
                if (manager.add(node_name, name)):
                    return jsonify({"status":"success", "type_name":type_name})
            elif(type_name == "REMOVE"):
                if (manager.remove(node_name, name)):
                    return jsonify({"status":"success", "type_name":type_name})
            elif(type_name == "GET"):
                response_data = manager.get(node_name, name)
                response_data["status"] = "success"
                response_data["type_name"] = type_name
                return jsonify(response_data)
            return jsonify({"status":"unsuccess", "type_name":type_name})

        except Exception as e:
            logger.error(e)
            return jsonify({"status":"unsuccess", "type_name":type_name})

def add_url_rule(app):
    api = __template.as_view(f'gpu')
    app.add_url_rule(f'/gpu/<method>', view_func=api, methods=["POST"])
