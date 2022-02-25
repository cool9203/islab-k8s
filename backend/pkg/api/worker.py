import logging
logger = logging.getLogger(__name__)

#from pkg.api import
from pkg.api import test
from pkg.api import pv_creater

def add_url_rule(app):
    test.add_url_rule(app)
    pv_creater.add_url_rule(app)
