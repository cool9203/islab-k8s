import importlib
import logging
logger = logging.getLogger(__name__)

using_api_name_list = ["test", "get-worker", "test-worker"]


api_list = list()
for api_name in using_api_name_list:
    api = importlib.import_module(f"pkg.api.{api_name}")
    logger.info(f"load api : {api.__name__}")
    api_list.append(api)


def add_url_rule(app):
    for api in api_list:
        api.add_url_rule(app)
