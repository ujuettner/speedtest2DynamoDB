#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: Run a lint tool.

import sys
import logging
import subprocess

def parse_output(output_lines):
    # TODO: Implement parsing.
    ping_ms = download_bit_per_second = upload_bit_per_second = -1
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
