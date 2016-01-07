#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Runs speedtest-cli (https://github.com/sivel/speedtest-cli), parses its
   output and writes the values to Amazon DynamoDB."""

import sys
import logging
import logging.handlers
import time
import subprocess
import re
import uuid
import decimal
import boto3
from botocore.exceptions import ClientError


_LOG_FILENAME = '/tmp/speedtest2DynamoDB.log'
_LOG_LEVEL = logging.DEBUG
_LOG_MAX_BYTES = 1024 * 1024
_LOG_BACKUP_COUNT = 9
_DYNAMODB_TABLE_NAME = 'speedtestresults'
_DYNAMODB_RCU = 5
_DYNAMODB_WCU = 5
_DYNAMODB_TRIES = 3
_DYNAMODB_RETRY_SLEEP_BASE_SECS = 30
_LOGGER = logging.getLogger(__name__)
_DYNAMODB = boto3.resource('dynamodb')


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
        _LOGGER.exception('Unable to parse - using default value.')

    try:
        download_match = download_pattern.match(output_lines)
        download_bit_per_second = _normalize_to_bit_per_second(
            download_match.group(1),
            download_match.group(2)
        )
    except AttributeError:
        _LOGGER.exception('Unable to parse - using default value.')

    try:
        upload_match = upload_pattern.match(output_lines)
        upload_bit_per_second = _normalize_to_bit_per_second(
            upload_match.group(1),
            upload_match.group(2)
        )
    except AttributeError:
        _LOGGER.exception('Unable to parse - using default value.')

    return (ping_ms, download_bit_per_second, upload_bit_per_second)


def _create_dynamodb_table(table_name):
    """Create the table in DynamoDB."""
    table = _DYNAMODB.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': _DYNAMODB_RCU,
            'WriteCapacityUnits': _DYNAMODB_WCU
        }
    )
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    table.reload()
    _LOGGER.info(
        'DynamoDB table {} created. Status: {}. Number of items: {}.'.
        format(table_name, table.table_status, table.item_count)
    )


def _table_exists(table_name):
    """Checks whether a DynamoDB table exists."""
    return len([t for t in _DYNAMODB.tables.all() if t.name == table_name]) > 0


def write_to_dynamodb(table_name,
                      timestamp,
                      ping_ms,
                      download_bit_per_second,
                      upload_bit_per_second):
    """Write given values to DynamoDB."""
    if not _table_exists(table_name):
        _create_dynamodb_table(table_name)

    table = _DYNAMODB.Table(_DYNAMODB_TABLE_NAME)
    try_count = 0
    while try_count < _DYNAMODB_TRIES:
        try:
            table.put_item(
                Item={
                    'id': str(uuid.uuid4()),
                    'timestamp': decimal.Decimal(str(timestamp)),
                    'ping_ms': decimal.Decimal(str(ping_ms)),
                    'download_bit_per_second':
                        decimal.Decimal(str(download_bit_per_second)),
                    'upload_bit_per_second':
                        decimal.Decimal(str(upload_bit_per_second))
                }
            )
        except ClientError:
            wait_time = (2 ** try_count) * _DYNAMODB_RETRY_SLEEP_BASE_SECS
            try_count += 1
            _LOGGER.warn(
                'Try {}/{} to write to table {} failed.'.
                format(try_count, _DYNAMODB_TRIES, table_name)
            )
            if try_count < _DYNAMODB_TRIES:
                _LOGGER.info(
                    'Waiting {} seconds before re-trying ...'.
                    format(wait_time)
                )
                time.sleep(wait_time)
        else:
            break


def main():
    """The main entry point."""
    _LOGGER.setLevel(_LOG_LEVEL)
    log_handler = logging.handlers.RotatingFileHandler(
        _LOG_FILENAME,
        maxBytes=_LOG_MAX_BYTES,
        backupCount=_LOG_BACKUP_COUNT
    )
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log_handler.setFormatter(log_formatter)
    _LOGGER.addHandler(log_handler)
    timestamp = time.time()
    _LOGGER.info('Starting at {} ...'.format(timestamp))
    try:
        external_speedtest_cli_output = subprocess.check_output(
            ['../speedtest-cli/speedtest_cli.py', '--simple'],
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as cpe:
        _LOGGER.error(
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

    _LOGGER.debug('OUTPUT:\n{}'.format(external_speedtest_cli_output))
    ping_ms, download_bit_per_second, upload_bit_per_second = parse_output(
        external_speedtest_cli_output
    )
    _LOGGER.debug(
        'PARSED:\nping [ms]: {}\ndownload [bit/s]: {}\nupload [bits/s]: {}'.
        format(ping_ms, download_bit_per_second, upload_bit_per_second)
    )
    _LOGGER.info(
        'Writing to DynamoDB table {} ...'.
        format(_DYNAMODB_TABLE_NAME)
    )
    write_to_dynamodb(
        _DYNAMODB_TABLE_NAME,
        timestamp,
        ping_ms,
        download_bit_per_second,
        upload_bit_per_second
    )
    _LOGGER.info('Finished.')

if __name__ == '__main__':
    main()

# vim:ts=4:sw=4:expandtab
