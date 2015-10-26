#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: Run a lint tool.

import sys

'''
import os
speedtest_cli = "../speedtest-cli"
sys.path.append(os.path.abspath(speedtest_cli))
from speedtest_cli import *
speedtest()
'''

# https://docs.python.org/2/library/subprocess.html
import subprocess

try:
    external_speedtest_cli_output = subprocess.check_output(["../speedtest-cli/speedtest_cli.py", "--simple"], stderr=subprocess.STDOUT)
except subprocess.CalledProcessError as e:
    print "Ooops!\nCommand\n\t{}\nreturned with exit code\n\t{}\n.\nCommand's output:\n{}".format(e.cmd, e.returncode, e.output)
    sys.exit(1)

print "OUTPUT:\n{}".format(external_speedtest_cli_output)
#OUTPUT:
#Ping: 54.115 ms
#Download: 8.01 Mbit/s
#Upload: 5.81 Mbit/s

# TODO: virtualenv + pip
# TODO: Create table and define schema.
# TODO: https://github.com/boto/boto3 + https://boto3.readthedocs.org/en/latest/reference/services/dynamodb.html
# TODO: Ansible

# vim:ts=4:sw=4:expandtab
