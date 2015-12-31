import unittest
from speedtest2DynamoDB import *

class SpeedTest2DynamoDBTestCase(unittest.TestCase):

    def test_parse_output_bit(self):
        self.assertEqual(
                parse_output('Ping: 10.331 ms\nDownload: 40.5 bit/s\nUpload: 5.88 Bit/s'),
                (10.331, 40.5, 5.88)
        )

    def test_parse_output_kbit(self):
        self.assertEqual(
                parse_output('Ping: 10.331 ms\nDownload: 40.53 Kbit/s\nUpload: 5.88 kbit/s'),
                (10.331, 41502.72, 6021.12)
        )

    def test_parse_output_mbit(self):
        self.assertEqual(
                parse_output('Ping: 10.331 ms\nDownload: 40.53 mbit/s\nUpload: 5.88 Mbit/s'),
                (10.331, 42498785.28, 6165626.88)
        )

    def test_parse_output_gbit(self):
        self.assertEqual(
                parse_output('Ping: 10.331 ms\nDownload: 40.53 Gbit/s\nUpload: 5.88 gbit/s'),
                (10.331, 43518756126.72, 6313601925.12)
        )

    def test_parse_output_mixed_bit(self):
        self.assertEqual(
                parse_output('Ping: 10.331 ms\nDownload: 40.53 Gbit/s\nUpload: 5.88 bit/s'),
                (10.331, 43518756126.72, 5.88)
        )

    def test_parse_output_swapped_order(self):
        self.assertEqual(
                parse_output('Upload: 5.88 bit/s\nPing: 10.331 ms\nDownload: 40.53 bit/s'),
                (10.331, 40.53, 5.88)
        )

    def test_parse_output_not_matching(self):
        self.assertEqual(
                parse_output('Ping: 10.331 s\nDownload: 40.xx bit/s\nUpload: 5.88 m/s'),
                (-1, -1, -1)
        )

if __name__ == '__main__':
    unittest.main()
