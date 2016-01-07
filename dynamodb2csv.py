#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Exports Amazon DynamoDB table items to CSV."""

from __future__ import print_function
import boto3
import datetime


_DYNAMODB_TABLE_NAME = 'speedtestresults'
_FIELDS = [
    'id',
    'timestamp',
    'ping_ms',
    'download_bit_per_second',
    'upload_bit_per_second'
]
_FIELD_SEPARATOR = ','


def main():
    """The main entry point."""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(_DYNAMODB_TABLE_NAME)
    response = table.scan()
    print(_FIELD_SEPARATOR.join(_FIELDS))
    for item in response['Items']:
        record_items = list()
        for field in _FIELDS:
            if field == 'timestamp':
                record_items.append(
                    datetime.datetime.fromtimestamp(
                        item[field]
                    ).strftime('%Y-%m-%d %H:%M:%S')
                )
            else:
                record_items.append(str(item[field]))
        print(_FIELD_SEPARATOR.join(record_items))

if __name__ == '__main__':
    main()

# vim:ts=4:sw=4:expandtab
