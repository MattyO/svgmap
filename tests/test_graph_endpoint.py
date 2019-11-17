import unittest
from datetime import datetime

from app import scale, to_timestamp

class GraphTest(unittest.TestCase):

    def setUp(self):
        self.a =[[0, 1],[50, 2],[100, 3]] 
        self.min_max = [
                min(self.a, key=lambda i: i[0])[0],
                max(self.a, key=lambda i: i[0])[0]
        ]

    def test_simple(self):
        new_data = scale(self.a, 0, self.min_max, [0, 200])
        self.assertEqual(new_data, [[0, 1], [100, 2], [200,3]])

    def test_starting_non_zero(self):
        new_data = scale(self.a, 0, self.min_max, [100, 300])
        self.assertEqual(new_data, [[100, 1], [200, 2], [300, 3]])

    def test_negative_scale(self):
        new_scale = [100, 0]

        new_data = scale(self.a, 0, self.min_max, new_scale)
        self.assertEqual(new_data, [[100,1], [50, 2], [0, 3]])

    def test_more_complicate(self):
        new_scale = [0, 200]
        self.a =[[0, 1],[75, 2],[100, 3]] 

        new_data = scale(self.a, 0, self.min_max, new_scale)
        self.assertEqual(new_data, [[0, 1], [150, 2], [200, 3]])

    def test_to_timestamp(self):
        self.assertEqual(to_timestamp([['01-01-2018']], 0), [[datetime(2018, 1,1).timestamp()]])

    def test_to_timestamp_with_larger_array(self):
        self.assertEqual(to_timestamp([['01-01-2018', None]], 0), [[datetime(2018, 1,1).timestamp(), None]])

    def test_to_timestamp_with_larger_array_backwards(self):
        self.assertEqual(to_timestamp([[None, '01-01-2018']], 1), [[None, datetime(2018, 1,1).timestamp()]])

