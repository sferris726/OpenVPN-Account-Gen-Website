#! /usr/bin/python3.6

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/')
from FlaskApps.app import app as application
application.secret_key = 'yeah buddy'
