import unittest

from src.cli.main import KindleClippingsProcessor


class TestRemoveDuplicates(unittest.TestCase):
    def setUp(self):
        """Set up a KindleClippingsProcessor instance for testing."""
        self.processor = KindleClippingsProcessor(None)

    def test_no_duplicates(self):
        """Test with no overlapping highlights."""
        clippings = [
            "Test Book (Author A)\n- Your Highlight on Location 100-110 | Added on Date\n\ncontent",
            "Test Book (Author A)\n- Your Highlight on Location 200-210 | Added on Date\n\ncontent",
        ]
        result = self.processor.remove_duplicates(clippings)
        self.assertEqual(len(result), 2)
        self.assertIn(clippings[0], result)
        self.assertIn(clippings[1], result)

    def test_exact_duplicates(self):
        """Test with exact duplicate highlights."""
        clippings = [
            "Test Book (Author A)\n- Your Highlight on Location 100-110 | Added on Date\n\ncontent",
            "Test Book (Author A)\n- Your Highlight on Location 100-110 | Added on Date\n\ncontent",
        ]
        result = self.processor.remove_duplicates(clippings)
        self.assertEqual(len(result), 1)
        self.assertIn(clippings[1], result)

    def test_partial_overlaps(self):
        """Test with partially overlapping highlights."""
        clippings = [
            "Test Book (Author A)\n- Your Highlight on Location 100-110 | Added on Date\n\ncontent",
            (
                "Test Book (Author A)\n- Your Highlight on Location 105-115 | Added on"
                " Date\n\nlonger content"
            ),
        ]
        result = self.processor.remove_duplicates(clippings)
        self.assertEqual(len(result), 1)
        self.assertIn(clippings[1], result)

    def test_non_highlights(self):
        """Test with non-highlight entries like notes and bookmarks."""
        clippings = [
            "Test Book (Author A)\n- Your Note on Location 100 | Added on Date\n\ncontent",
            "Test Book (Author A)\n- Your Bookmark on Location 200 | Added on Date\n\ncontent",
        ]
        result = self.processor.remove_duplicates(clippings)
        self.assertEqual(len(result), 2)
        self.assertIn(clippings[0], result)
        self.assertIn(clippings[1], result)

    def test_mixed_entries(self):
        """Test with a mix of highlights, notes, and bookmarks."""
        clippings = [
            "Test Book (Author A)\n- Your Highlight on Location 100-110 | Added on Date\n\ncontent",
            "Test Book (Author A)\n- Your Note on Location 100 | Added on Date\n\nnote content",
            (
                "Test Book (Author A)\n- Your Bookmark on Location 200 | Added on Date\n\nbookmark"
                " content"
            ),
            (
                "Test Book (Author A)\n- Your Highlight on Location 105-115 | Added on"
                " Date\n\nlonger content"
            ),
        ]
        result = self.processor.remove_duplicates(clippings)
        self.assertEqual(len(result), 3)
        self.assertIn(clippings[1], result)
        self.assertIn(clippings[2], result)
        self.assertIn(clippings[3], result)

    def test_adjacent_highlights(self):
        """Test with adjacent highlights that should not be considered duplicates."""
        clippings = [
            (
                "Generic Book (Author A)\n- Your Highlight on Location 100-110 | Added on"
                " Date\nContent A"
            ),
            (
                "Generic Book (Author A)\n- Your Highlight on Location 110-115 | Added on"
                " Date\nContent B"
            ),
        ]
        result = self.processor.remove_duplicates(clippings)
        self.assertEqual(len(result), 2)
        self.assertIn(clippings[0], result)
        self.assertIn(clippings[1], result)

    def test_overlapping_and_non_overlapping(self):
        """Test with a combination of overlapping and non-overlapping highlights."""
        clippings = [
            "Test Book (Author A)\n- Your Highlight on Location 100-110 | Added on Date\nContent A",
            "Test Book (Author A)\n- Your Highlight on Location 110-115 | Added on Date\nContent B",
            "Test Book (Author A)\n- Your Highlight on Location 115-120 | Added on Date\nContent C",
        ]
        result = self.processor.remove_duplicates(clippings)
        self.assertEqual(len(result), 3)
        self.assertIn(clippings[0], result)
        self.assertIn(clippings[1], result)
        self.assertIn(clippings[2], result)


if __name__ == "__main__":
    unittest.main()
