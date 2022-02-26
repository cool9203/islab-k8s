import logging

logger = logging.getLogger(__name__)

from pkg.api import util
from flask import Flask, jsonify
from flask.views import MethodView


class machine(MethodView):
    def post(self, method):
        if (not method in ["ADD", "REMOVE", "GET"]):
            return jsonify({"status":"unsuccess"})

        try:
            data = util.get_request_data()
            logger.info(f"get method:{method}")

            if (method == "ADD"):
                return jsonify({"status":"success", "data":method})
            elif(method == "REMOVE"):
                return jsonify({"status":"success", "data":method})
            elif(method == "GET"):
                return jsonify({"status":"success", "data":method})
            return jsonify({"status":"unsuccess"})

        except Exception as e:
            logger.error(e)
            return jsonify({"status":"unsuccess"})

    def get(self, method):
        if (not method in ["ADD", "REMOVE", "GET"]):
            return jsonify({"status":"unsuccess"})

        logger.info(f"get method:{method}")

        return jsonify({"status":"success", "data":method})
        

def add_url_rule(app):
    api = machine.as_view(f'machine')
    app.add_url_rule(f'/machine/<method>', view_func=api, methods=["POST"])
