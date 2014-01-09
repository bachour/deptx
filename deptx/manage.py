#!/usr/bin/env python
import os
import sys
import socket
from django.utils.log import getLogger
from django.core.management import execute_from_command_line
from deptx.secrets import PRODUCTION_HOSTNAME

try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'exception'

logger = getLogger('management_commands')

if __name__ == "__main__":
    if HOSTNAME == PRODUCTION_HOSTNAME:
        #print 'production'
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deptx.settings_production")
    else:
        #print 'local'
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deptx.settings")

    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        logger.error('Admin Command Error: %s', ' '.join(sys.argv), exc_info=sys.exc_info())
        raise e
