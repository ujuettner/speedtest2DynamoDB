# speedtest2DynamoDB

`speedtest2dynamodb.py` runs [speedtest-cli](https://github.com/sivel/speedtest-cli), parses its output and writes the values to Amazon DynamoDB.

It uses [Boto3](https://github.com/boto/boto3). Therefore, it relies on a properly set up `~/.aws/credentials` and `~/.aws/config`, respectively.
