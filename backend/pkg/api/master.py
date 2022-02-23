import logging
logger = logging.getLogger(__name__)

#from pkg.api import
from pkg.api import test
from pkg.api import get_worker
from pkg.api import test_worker

def add_url_rule(app):
    test.add_url_rule(app)
    get_worker.add_url_rule(app)
    test_worker.add_url_rule(app)
