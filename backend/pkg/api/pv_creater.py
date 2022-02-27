import logging

logger = logging.getLogger(__name__)

from pkg.api import util
from flask import Flask, jsonify
from flask.views import MethodView
from pathlib import Path


class pv_creater(MethodView):
    def get(self, method, pod_name):
        if (not method in ["ADD"]):
            return jsonify({"status":"unsuccess"})

        pv_path = Path("./pv-storage", pod_name)
        try:
            if (method == "ADD"):
                pv_path.mkdir(exist_ok=True)
            elif (method == "DELETE"):
                for file_name in pv_path.iterdir():
                    Path(pv_path, file_name).unlink()
                pv_path.rmdir()

            return jsonify({"status":"success"})
        except Exception as e:
            return jsonify({"status":"unsuccess"})
        

def add_url_rule(app):
    api = pv_creater.as_view(f'pv_creater')
    app.add_url_rule(f'/pv_creater/<method>/pod_name/<pod_name>', view_func=api, methods=["GET"])
