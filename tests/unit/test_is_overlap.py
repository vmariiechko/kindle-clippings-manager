import unittest
from src.cli.main import KindleClippingsProcessor


class TestOverlapDetection(unittest.TestCase):
    def setUp(self):
        """Set up a KindleClippingsProcessor instance for testing."""
        self.processor = KindleClippingsProcessor(None)

    def test_exact_overlap(self):
        """Test for exact overlap between two ranges."""
        self.assertTrue(self.processor.is_overlap((100, 110), (100, 110)))

    def test_partial_overlap_within(self):
        """Test for partial overlap where one range is within another."""
        self.assertTrue(self.processor.is_overlap((100, 110), (105, 108)))

    def test_partial_overlap_extending(self):
        """Test for partial overlaps where ranges extend beyond each other."""
        self.assertTrue(self.processor.is_overlap((100, 110), (95, 105)))
        self.assertTrue(self.processor.is_overlap((100, 110), (105, 115)))

    def test_full_encapsulation(self):
        """Test for one range fully encapsulating another."""
        self.assertTrue(self.processor.is_overlap((100, 110), (95, 115)))

    def test_single_point_overlap(self):
        """Test for overlap at a single point."""
        self.assertTrue(self.processor.is_overlap((100, 110), (105, 105)))

    def test_no_overlap(self):
        """Test for no overlap between two ranges."""
        self.assertFalse(self.processor.is_overlap((100, 110), (120, 125)))

    def test_adjacent_no_overlap(self):
        """Test for no overlap with adjacent ranges."""
        self.assertFalse(self.processor.is_overlap((100, 110), (110, 120)))
        self.assertFalse(self.processor.is_overlap((100, 110), (110, 110)))

    def test_start_and_end_overlap(self):
        """Test for no overlap when one range starts or ends where another ends or starts."""
        self.assertFalse(self.processor.is_overlap((100, 110), (110, 110)))
        self.assertFalse(self.processor.is_overlap((100, 110), (100, 100)))


if __name__ == "__main__":
    unittest.main()
