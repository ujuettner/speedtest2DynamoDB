#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Runs speedtest-cli (https://github.com/sivel/speedtest-cli), parses its
   output and writes the values to Amazon DynamoDB."""

import sys
import logging
import logging.handlers
import subprocess
import re


logger = logging.getLogger(__name__)


def _normalize_to_bit_per_second(value, unit):
    """Return given value as bit/s depending on given
       unit."""
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
    """Parse command output and return a tuple containing the ping time in ms,
       the download and the upload speed (both as bit/s)."""
    ping_ms = download_bit_per_second = upload_bit_per_second = -1

    ping_pattern = re.compile(
        r'.*Ping: (\d+\.?\d*) ms.*',
        re.DOTALL
    )
    download_pattern = re.compile(
        r'.*Download: (\d+\.?\d+) (\w+)/s.*',
        re.DOTALL
    )
    upload_pattern = re.compile(
        r'.*Upload: (\d+\.?\d+) (\w+)/s.*',
        re.DOTALL
    )

    try:
        ping_match = ping_pattern.match(output_lines)
        ping_ms = float(ping_match.group(1))
    except AttributeError:
        logger.exception('Unable to parse - using default value.')

    try:
        download_match = download_pattern.match(output_lines)
        download_bit_per_second = _normalize_to_bit_per_second(
            download_match.group(1),
            download_match.group(2)
        )
    except AttributeError:
        logger.exception('Unable to parse - using default value.')

    try:
        upload_match = upload_pattern.match(output_lines)
        upload_bit_per_second = _normalize_to_bit_per_second(
            upload_match.group(1),
            upload_match.group(2)
        )
    except AttributeError:
        logger.exception('Unable to parse - using default value.')

    return (ping_ms, download_bit_per_second, upload_bit_per_second)


def main():
    """The main entry point."""
    # TODO: Let the log level be set via command line options.
    LOG_FILENAME = '/tmp/speedtest2DynamoDB.log'
    logger.setLevel(logging.DEBUG)
    log_handler = logging.handlers.RotatingFileHandler(
        LOG_FILENAME,
        maxBytes=1024,
        backupCount=10
    )
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    logger.info('Starting ...')
    try:
        external_speedtest_cli_output = subprocess.check_output(
            ['../speedtest-cli/speedtest_cli.py', '--simple'],
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as cpe:
        logger.error(
            """Ooops!
Command
\t{}
returned with exit code
\t{}
.
Command output:
{}""".
            format(cpe.cmd, cpe.returncode, cpe.output)
        )
        sys.exit(1)

    logger.debug('OUTPUT:\n{}'.format(external_speedtest_cli_output))
    ping_ms, upload_bit_per_second, download_bit_per_second = parse_output(
        external_speedtest_cli_output
    )
    logger.debug(
        'PARSED:\nping [ms]: {}\ndownload [bit/s]: {}\nupload [bits/s]: {}'.
        format(ping_ms, download_bit_per_second, upload_bit_per_second)
    )
    logger.info('Finished.')

if __name__ == '__main__':
    main()

# TODO: virtualenv + pip
# TODO: Create table and define schema.
# TODO: https://github.com/boto/boto3
#       https://boto3.readthedocs.org/en/latest/reference/services/dynamodb.html
# TODO: Ansible

# vim:ts=4:sw=4:expandtab
