#!/usr/bin/env python
import os
import sys
import socket
from deptx.secrets import PRODUCTION_HOSTNAME

try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'exception'

print HOSTNAME

if __name__ == "__main__":
    if HOSTNAME == PRODUCTION_HOSTNAME:
        print 'production'
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deptx.settings_production")
    else:
        print 'local'
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deptx.settings")
    
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
