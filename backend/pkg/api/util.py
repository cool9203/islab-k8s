import logging
logger = logging.getLogger(__name__)

from flask import request
import requests
import json

def get_request_data():
    #get data, and all data key change to capital letter
    json_data = request.data.decode("utf-8").replace("\'", "\"")
    form_data = request.form.to_dict(flat=False)
    logger.debug(f"get json_data : {json_data}")
    logger.debug(f"get form_data : {form_data}")
    data = dict()
    try:
        data = json.loads(json_data)
    except:
        pass

    data.update(form_data)

    logger.debug(f"get data : {data}")
    data = {k.upper():v for k, v in data.items()}
    return data


def call_api(api_url, method, data={}, headers={"Content-Type": "application/json"}):
    if (not method in ["POST", "GET"]):
        raise Exception("method error")
    
    if (method == "POST"):
        req = requests.post(api_url, data=json.dumps(data), headers=headers)
    else:
        req = requests.get(api_url)
    return req.text
