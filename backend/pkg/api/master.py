import logging
logger = logging.getLogger(__name__)

using_api_name_list = ["test", "get-worker", "test-worker"]

from pkg.api import test, get_worker, test_worker

def add_url_rule(app):
    test.add_url_rule(app)
    get-worker.add_url_rule(app)
    test-worker.add_url_rule(app)
