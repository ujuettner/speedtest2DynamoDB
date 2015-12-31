"""Test cases."""
import unittest
from speedtest2dynamodb import parse_output


class SpeedTest2DynamoDBTestCase(unittest.TestCase):
    """Collection of tests."""

    def test_parse_output_bit(self):
        """Test output that contains only bit/s."""
        self.assertEqual(
            parse_output(
                'Ping: 10.331 ms\nDownload: 40.5 bit/s\nUpload: 5.88 Bit/s'
            ),
            (10.331, 40.5, 5.88)
        )

    def test_parse_output_kbit(self):
        """Test output that contains only Kbit/s."""
        self.assertEqual(
            parse_output(
                'Ping: 10.331 ms\nDownload: 40.53 Kbit/s\nUpload: 5.88 kbit/s'
            ),
            (10.331, 41502.72, 6021.12)
        )

    def test_parse_output_mbit(self):
        """Test output that contains only Mbit/s."""
        self.assertEqual(
            parse_output(
                'Ping: 10.331 ms\nDownload: 40.53 mbit/s\nUpload: 5.88 Mbit/s'
            ),
            (10.331, 42498785.28, 6165626.88)
        )

    def test_parse_output_gbit(self):
        """Test output that contains only Gbit/s."""
        self.assertEqual(
            parse_output(
                'Ping: 10.331 ms\nDownload: 40.53 Gbit/s\nUpload: 5.88 gbit/s'
            ),
            (10.331, 43518756126.72, 6313601925.12)
        )

    def test_parse_output_mixed_bit(self):
        """Test output that contains bit/s and Gbit/s."""
        self.assertEqual(
            parse_output(
                'Ping: 10.331 ms\nDownload: 40.53 Gbit/s\nUpload: 5.88 bit/s'
            ),
            (10.331, 43518756126.72, 5.88)
        )

    def test_parse_output_swapped_order(self):
        """Test output with changed order."""
        self.assertEqual(
            parse_output(
                'Upload: 5.88 bit/s\nPing: 10.331 ms\nDownload: 40.53 bit/s'
            ),
            (10.331, 40.53, 5.88)
        )

    def test_parse_output_not_matching(self):
        """Test whether default values are returned when unable to parse."""
        self.assertEqual(
            parse_output(
                'Ping: 10.331 s\nDownload: 40.xx bit/s\nUpload: 5.88 m/s'
            ),
            (-1, -1, -1)
        )

if __name__ == '__main__':
    unittest.main()
