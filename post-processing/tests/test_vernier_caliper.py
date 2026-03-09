# ------------------------------------------------------------------------------
#  (c) Crown copyright Met Office. All rights reserved.
#  The file LICENCE, distributed with this code, contains details of the terms
#  under which the code may be used.
# ------------------------------------------------------------------------------
import unittest
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from vernier.vernier_data import VernierCaliper

class TestVernierCaliper(unittest.TestCase):

    def setUp(self):
        self.caliper_a = VernierCaliper("test_caliper_a", 2)
        self.caliper_b = VernierCaliper("test_caliper_b", 2)

    def test_init(self):
        self.assertEqual(self.caliper_a.name, "test_caliper_a")
        self.assertTrue(np.array_equal(self.caliper_a.time_percent, np.array([0.0, 0.0])))
        self.assertTrue(np.array_equal(self.caliper_a.cumul_time, np.array([0.0, 0.0])))
        self.assertTrue(np.array_equal(self.caliper_a.self_time, np.array([0.0, 0.0])))
        self.assertTrue(np.array_equal(self.caliper_a.total_time, np.array([0.0, 0.0])))
        self.assertTrue(np.array_equal(self.caliper_a.n_calls, np.array([0.0, 0.0])))

    def test_reduce(self):
        self.caliper_a.time_percent = np.array([10.0, 20.0])
        self.caliper_a.cumul_time = np.array([30.0, 40.0])
        self.caliper_a.self_time = np.array([5.0, 15.0])
        self.caliper_a.total_time = np.array([25.0, 35.0])
        self.caliper_a.n_calls = np.array([2, 2])

        reduced_data = self.caliper_a.reduce()
        self.assertEqual(reduced_data[0], "test_caliper_a")
        self.assertEqual(reduced_data[1], 30.0)
        self.assertEqual(reduced_data[2], 10.0)
        self.assertEqual(reduced_data[3], 35.0)
        self.assertEqual(reduced_data[4], 2)
        self.assertEqual(reduced_data[5], 15.0)
        self.assertEqual(reduced_data[6], 15.0)

    def test_compare(self):
        self.caliper_a.time_percent = np.array([10.0, 20.0])
        self.caliper_a.cumul_time = np.array([30.0, 40.0])
        self.caliper_a.self_time = np.array([5.0, 15.0])
        self.caliper_a.total_time = np.array([25.0, 35.0])
        self.caliper_a.n_calls = np.array([2, 2])

        self.caliper_b.time_percent = np.array([12.0, 25.0])
        self.caliper_b.cumul_time = np.array([35.0, 46.0])
        self.caliper_b.self_time = np.array([6.0, 19.0])
        self.caliper_b.total_time = np.array([28.0, 39.0])
        self.caliper_b.n_calls = np.array([2, 2])

        self.assertTrue(self.caliper_a < self.caliper_b)
        self.assertFalse(self.caliper_a > self.caliper_b)
        self.assertFalse(self.caliper_a == self.caliper_b)

if __name__ == '__main__':
    unittest.main()
