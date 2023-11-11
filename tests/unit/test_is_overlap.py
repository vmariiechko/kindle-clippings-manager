import unittest

from src.cli.main import is_overlap


class TestOverlapDetection(unittest.TestCase):
    def test_exact_overlap(self):
        """Test for exact overlap between two ranges."""
        self.assertTrue(is_overlap((100, 110), (100, 110)))

    def test_partial_overlap_within(self):
        """Test for partial overlap where one range is within another."""
        self.assertTrue(is_overlap((100, 110), (105, 108)))

    def test_partial_overlap_extending(self):
        """Test for partial overlaps where ranges extend beyond each other."""
        self.assertTrue(is_overlap((100, 110), (95, 105)))
        self.assertTrue(is_overlap((100, 110), (105, 115)))

    def test_full_encapsulation(self):
        """Test for one range fully encapsulating another."""
        self.assertTrue(is_overlap((100, 110), (95, 115)))

    def test_single_point_overlap(self):
        """Test for overlap at a single point."""
        self.assertTrue(is_overlap((100, 110), (105, 105)))

    def test_no_overlap(self):
        """Test for no overlap between two ranges."""
        self.assertFalse(is_overlap((100, 110), (120, 125)))

    def test_adjacent_no_overlap(self):
        """Test for no overlap with adjacent ranges."""
        self.assertFalse(is_overlap((100, 110), (110, 120)))
        self.assertFalse(is_overlap((100, 110), (110, 110)))

    def test_start_and_end_overlap(self):
        """Test for no overlap when one range starts or ends where another ends or starts."""
        self.assertFalse(is_overlap((100, 110), (110, 110)))
        self.assertFalse(is_overlap((100, 110), (100, 100)))


if __name__ == "__main__":
    unittest.main()
