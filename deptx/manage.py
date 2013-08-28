#!/usr/bin/env python
import os
import sys
import socket

try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost.local'

if __name__ == "__main__":
    if '.local' in HOSTNAME:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deptx.settings")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deptx.settings_production")
    
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
