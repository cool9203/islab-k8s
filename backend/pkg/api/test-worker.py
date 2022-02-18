import logging

logger = logging.getLogger(__name__)

from pkg.api import util
from flask import Flask, jsonify
from flask.views import MethodView
import pkg.kubeapi
import pkg.log

kubeapi = pkg.kubeapi.__kubeapi()
setting = pkg.log.load_setting("./setting.txt")


class test_worker(MethodView):
    def get(self, method):
        if (not method in ["GET"]):
            return jsonify({"status":"unsuccess"})
        try:
            all_worker = kubeapi.get_all_worker(setting["WORKER_NAME"])
            for worker_name, spec in all_worker.items():
                pod_ip = spec["pod_ip"]
                logger.info(f"worker_name {worker_name} : {pod_ip}")
                ret = util.call_api(f"http://{pod_ip}:8080/test/GET", "GET")
                logger.info(f"{worker_name}:{ret}")

            return jsonify({"status":"success", "data":all_worker})
        
        except Exception as e:
            logger.error(e)
            return jsonify({"status":"unsuccess"})
        

def add_url_rule(app):
    _api = test_worker.as_view(f'test_worker')
    app.add_url_rule(f'/test-worker/<method>', view_func=_api, methods=["GET"])
