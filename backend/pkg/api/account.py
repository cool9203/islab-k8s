import logging

logger = logging.getLogger(__name__)

from pkg.api import util
from flask import Flask, jsonify
from flask.views import MethodView
import pkg.dbapi


class account(MethodView):
    def post(self, method):
        if (not method in ["LOGIN"]):
            return jsonify({"status":"unsuccess"})

        try:
            data = util.get_request_data()

            if (method == "LOGIN"):
                try:
                    result = pkg.dbapi.login(data["uid".upper()], data["passwd".upper()])
                    result.update({"status":"success", "result":"success", "token":""})
                    return jsonify(result)
                except Exception as e:
                    logger.error(e)
                    return jsonify({"status":"success", "result":"failed"})
                
            return jsonify({"status":"unsuccess"})

        except Exception as e:
            logger.error(e)
            return jsonify({"status":"unsuccess"})


        

def add_url_rule(app):
    api = account.as_view(f'account')
    app.add_url_rule(f'/account/<method>', view_func=api, methods=["POST"])
