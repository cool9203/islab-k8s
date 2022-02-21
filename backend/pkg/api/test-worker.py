from pkg.api import util
from flask import Flask, jsonify
from flask.views import MethodView
import pkg.kubeapi
import pkg.log
import pkg.dbapi
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)
kubeapi = pkg.kubeapi.__kubeapi()

worker_name = pkg.dbapi.get_worker_name()
worker_port = pkg.dbapi.get_worker_port()

class test_worker(MethodView):
    def get(self, method):
        if (not method in ["GET"]):
            return jsonify({"status":"unsuccess"})
        try:
            all_worker = kubeapi.get_all_worker(worker_name)
            for name, spec in all_worker.items():
                pod_ip = spec["pod_ip"]
                logger.info(f"worker_name {name} : {pod_ip}")
                ret = util.call_api(f"http://{pod_ip}:{worker_port}/test/GET", "GET")
                logger.info(f"{worker_name}:{ret}")

            return jsonify({"status":"success", "data":all_worker})
        
        except Exception as e:
            logger.error(e)
            return jsonify({"status":"unsuccess"})
        

def add_url_rule(app):
    _api = test_worker.as_view(f'test_worker')
    app.add_url_rule(f'/test-worker/<method>', view_func=_api, methods=["GET"])
