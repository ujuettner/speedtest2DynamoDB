import unittest
from speedtest2DynamoDB import *

class SpeedTest2DynamoDBTestCase(unittest.TestCase):
    # TODO: Remove this dummy test.
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_parse_output(self):
        self.assertEqual(
                parse_output('Ping: 10.331 ms\nDownload: 40.53 Mbit/s\nUpload: 5.88 Mbit/s'),
                (10.331, 6165626.88, 42498785.28)
        )

    # TODO: Implement more tests: different order; bit, kbit, Mbit; bit vs byte; ...

if __name__ == '__main__':
    unittest.main()
