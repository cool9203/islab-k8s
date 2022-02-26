import logging
logger = logging.getLogger(__name__)

#from pkg.api import
from pkg.api import test
from pkg.api import get_worker
from pkg.api import test_worker
from pkg.api import account
from pkg.api import gpu
from pkg.api import machine
from pkg.api import pod

def add_url_rule(app):
    test.add_url_rule(app)
    get_worker.add_url_rule(app)
    test_worker.add_url_rule(app)
    account.add_url_rule(app)
    gpu.add_url_rule(app)
    machine.add_url_rule(app)
    pod.add_url_rule(app)
