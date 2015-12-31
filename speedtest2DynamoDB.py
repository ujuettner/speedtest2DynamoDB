#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: Run a lint tool.

import sys
import logging
import subprocess
import re

def _normalize_to_bit_per_second(value, unit):
    bit_per_second = -1

    if re.match('^bit', unit, flags=re.IGNORECASE):
        bit_per_second = float(value)
    elif re.match('^kbit', unit, flags=re.IGNORECASE):
        bit_per_second = float(value) * 1024
    elif re.match('^mbit', unit, flags=re.IGNORECASE):
        bit_per_second = float(value) * 1024 * 1024
    elif re.match('^gbit', unit, flags=re.IGNORECASE):
        bit_per_second = float(value) * 1024 * 1024 * 1024

    return bit_per_second

def parse_output(output_lines):
    ping_ms = download_bit_per_second = upload_bit_per_second = -1

    ping_pattern = re.compile(r'.*Ping: (\d+\.?\d*) ms.*', re.DOTALL)
    download_pattern = re.compile(r'.*Download: (\d+\.?\d+) (\w+)/s.*', re.DOTALL)
    upload_pattern = re.compile(r'.*Upload: (\d+\.?\d+) (\w+)/s.*', re.DOTALL)

    try:
        ping_match = ping_pattern.match(output_lines)
        ping_ms = float(ping_match.group(1))
    except Exception as e:
        logging.exception('Unable to parse - using default value.')
        pass

    try:
        download_match = download_pattern.match(output_lines)
        download_bit_per_second = _normalize_to_bit_per_second(download_match.group(1), download_match.group(2))
    except Exception as e:
        logging.exception('Unable to parse - using default value.')
        pass

    try:
        upload_match = upload_pattern.match(output_lines)
        upload_bit_per_second = _normalize_to_bit_per_second(upload_match.group(1), upload_match.group(2))
    except Exception as e:
        logging.exception('Unable to parse - using default value.')
        pass

    return (ping_ms, download_bit_per_second, upload_bit_per_second)

def main():
    # TODO: Let the log level be set via command line options.
    # TODO: What about log rotation?
    logging.basicConfig(
            filename='/tmp/speedtest2DynamoDB.log',
            format='%(asctime)s %(levelname)s %(message)s',
            level=logging.DEBUG
    )
    logging.info('Starting ...')
    try:
        external_speedtest_cli_output = subprocess.check_output(['../speedtest-cli/speedtest_cli.py', '--simple'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logging.error('Ooops!\nCommand\n\t{}\nreturned with exit code\n\t{}\n.\nCommand output:\n{}'.format(e.cmd, e.returncode, e.output))
        sys.exit(1)

    logging.debug('OUTPUT:\n{}'.format(external_speedtest_cli_output))
    ping_ms, upload_bit_per_second, download_bit_per_second = parse_output(external_speedtest_cli_output)
    logging.debug('PARSED:\nping [ms]: {}\ndownload [bit/s]: {}\nupload [bits/s]: {}'.format(ping_ms, download_bit_per_second, upload_bit_per_second))
    logging.info('Finished.')

if __name__ == '__main__':
    main()

# TODO: virtualenv + pip
# TODO: Create table and define schema.
# TODO: https://github.com/boto/boto3 + https://boto3.readthedocs.org/en/latest/reference/services/dynamodb.html
# TODO: Ansible

# vim:ts=4:sw=4:expandtab
