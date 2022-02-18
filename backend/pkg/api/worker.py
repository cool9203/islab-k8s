import importlib
import logging
logger = logging.getLogger(__name__)

using_api_name_list = ["test"]


api_list = list()
for api_name in using_api_name_list:
    try:
        api = importlib.import_module(f"pkg.api.{api_name}")
        api_list.append(api)
        logger.info(f"load api : {api.__name__}")
    except Exception as e:
        logger.error(e)


def add_url_rule(app):
    for api in api_list:
        api.add_url_rule(app)
