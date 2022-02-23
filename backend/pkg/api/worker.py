import logging
logger = logging.getLogger(__name__)

#from pkg.api import
from pkg.api import test

def add_url_rule(app):
    test.add_url_rule(app)
