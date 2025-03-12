import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.kindle.models import KindleClipping, ProcessedHighlight
from src.kindle.parsers import KindleClippingsParser
from src.kindle.processor import KindleClippingsProcessor


class TestKindleClippingsProcessor(unittest.TestCase):
    def setUp(self):
        """Set up a KindleClippingsProcessor instance for testing."""
        self.processor = KindleClippingsProcessor(Path("dummy_path.txt"))

        # Mock the parser
        self.processor.parser = MagicMock(spec=KindleClippingsParser)

        # Sample clippings for testing
        self.sample_clippings = [
            KindleClipping(
                book_title="Book A",
                content="Highlight content 1",
                location=(100, 110),
                location_text="100-110",
                added_date=datetime(2025, 2, 3, 8, 0, 0),
                is_highlight=True,
                is_note=False,
            ),
            KindleClipping(
                book_title="Book A",
                content="(Category) Note content 1",
                location=(110, 110),
                location_text="110",
                added_date=datetime(2025, 2, 3, 8, 1, 0),
                is_highlight=False,
                is_note=True,
            ),
            KindleClipping(
                book_title="Book A",
                content="Highlight content 2",
                location=(200, 210),
                location_text="200-210",
                added_date=datetime(2025, 2, 3, 9, 0, 0),
                is_highlight=True,
                is_note=False,
            ),
            KindleClipping(
                book_title="Book A",
                content="(Category>Subcategory) Note content 2",
                location=(209, 209),
                location_text="209",
                added_date=datetime(2025, 2, 3, 9, 1, 0),
                is_highlight=False,
                is_note=True,
            ),
            KindleClipping(
                book_title="Book B",
                content="Highlight content 3",
                location=(300, 310),
                location_text="300-310",
                added_date=datetime(2025, 2, 4, 8, 0, 0),
                is_highlight=True,
                is_note=False,
            ),
        ]

    def test_is_overlap(self):
        """Test overlap detection between ranges."""
        # Exact overlap
        self.assertTrue(self.processor.is_overlap((100, 110), (100, 110)))

        # Partial overlap
        self.assertTrue(self.processor.is_overlap((100, 110), (105, 115)))
        self.assertTrue(self.processor.is_overlap((100, 110), (95, 105)))

        # One range inside another
        self.assertTrue(self.processor.is_overlap((100, 110), (102, 108)))

        # No overlap
        self.assertFalse(self.processor.is_overlap((100, 110), (120, 130)))

        # Adjacent but not overlapping
        self.assertFalse(self.processor.is_overlap((100, 110), (110, 120)))
        self.assertFalse(self.processor.is_overlap((100, 110), (90, 100)))

    def test_remove_duplicates(self):
        """Test removing duplicate highlights."""
        # Create overlapping highlights
        clippings = [
            KindleClipping(
                book_title="Book A",
                content="Original highlight",
                location=(100, 110),
                location_text="100-110",
                added_date=datetime(2025, 2, 3, 8, 0, 0),
                is_highlight=True,
                is_note=False,
            ),
            KindleClipping(
                book_title="Book A",
                content="Overlapping highlight",
                location=(105, 115),
                location_text="105-115",
                added_date=datetime(2025, 2, 3, 9, 0, 0),
                is_highlight=True,
                is_note=False,
            ),
            KindleClipping(
                book_title="Book A",
                content="Non-overlapping highlight",
                location=(200, 210),
                location_text="200-210",
                added_date=datetime(2025, 2, 3, 10, 0, 0),
                is_highlight=True,
                is_note=False,
            ),
            KindleClipping(
                book_title="Book A",
                content="Note content",
                location=(110, 110),
                location_text="110",
                added_date=datetime(2025, 2, 3, 8, 1, 0),
                is_highlight=False,
                is_note=True,
            ),
        ]

        result = self.processor.remove_duplicates(clippings)

        # Should keep the newer overlapping highlight, the non-overlapping highlight, and the note
        self.assertEqual(len(result), 3)

        # Sort results by location for consistent testing
        sorted_results = sorted(result, key=lambda x: x.location[0])

        # Check items in order by location
        self.assertEqual(
            sorted_results[0].content, "Overlapping highlight"
        )  # Location starts at 105
        self.assertEqual(sorted_results[1].content, "Note content")  # Location is 110
        self.assertEqual(
            sorted_results[2].content, "Non-overlapping highlight"
        )  # Location starts at 200

    def test_process_clippings_with_matching_notes(self):
        """Test processing clippings with matching notes."""
        self.processor.parser.read_clippings.return_value = self.sample_clippings
        self.processor.parser.filter_by_book.return_value = self.sample_clippings[:4]  # Book A only

        processed = self.processor.process_clippings("Book A")

        self.assertEqual(len(processed), 2)  # Two highlights with notes

        # First highlight with note
        self.assertEqual(processed[0].highlight_text, "Highlight content 1")
        self.assertEqual(processed[0].note_text, "Note content 1")
        self.assertEqual(processed[0].categories[0][0], "Category")

        # Second highlight with note
        self.assertEqual(processed[1].highlight_text, "Highlight content 2")
        self.assertEqual(processed[1].note_text, "Note content 2")
        self.assertEqual(processed[1].categories[0][0], "Category")
        self.assertEqual(processed[1].categories[0][1], "Subcategory")

    def test_process_clippings_with_note_in_middle(self):
        """Test processing clippings with a note in the middle of a highlight."""
        clippings = [
            KindleClipping(
                book_title="Book A",
                content="Highlight spanning a range",
                location=(100, 120),
                location_text="100-120",
                is_highlight=True,
                is_note=False,
            ),
            KindleClipping(
                book_title="Book A",
                content="(Category) Note in the middle",
                location=(110, 110),
                location_text="110",
                is_highlight=False,
                is_note=True,
            ),
        ]

        self.processor.parser.read_clippings.return_value = clippings
        self.processor.parser.filter_by_book.return_value = clippings

        processed = self.processor.process_clippings("Book A")

        self.assertEqual(len(processed), 1)
        self.assertEqual(processed[0].highlight_text, "Highlight spanning a range")
        self.assertEqual(processed[0].note_text, "Note in the middle")
        self.assertEqual(processed[0].categories[0][0], "Category")

    def test_process_clippings_with_note_before_highlight(self):
        """Test processing clippings with a note added before its highlight."""
        clippings = [
            KindleClipping(
                book_title="Book A",
                content="(Category) Note added first",
                location=(110, 110),
                location_text="110",
                added_date=datetime(2025, 2, 3, 8, 0, 0),
                is_highlight=False,
                is_note=True,
            ),
            KindleClipping(
                book_title="Book A",
                content="Highlight added second",
                location=(110, 110),
                location_text="110-110",
                added_date=datetime(2025, 2, 3, 8, 1, 0),
                is_highlight=True,
                is_note=False,
            ),
        ]

        self.processor.parser.read_clippings.return_value = clippings
        self.processor.parser.filter_by_book.return_value = clippings

        processed = self.processor.process_clippings("Book A")

        self.assertEqual(len(processed), 1)
        self.assertEqual(processed[0].highlight_text, "Highlight added second")
        self.assertEqual(processed[0].note_text, "Note added first")
        self.assertEqual(processed[0].categories[0][0], "Category")

    def test_process_clippings_with_note_one_before_end(self):
        """Test processing clippings with a note one position before the end of a highlight."""
        clippings = [
            KindleClipping(
                book_title="Book A",
                content="Highlight with range",
                location=(100, 110),
                location_text="100-110",
                is_highlight=True,
                is_note=False,
            ),
            KindleClipping(
                book_title="Book A",
                content="(Category) Note one before end",
                location=(109, 109),
                location_text="109",
                is_highlight=False,
                is_note=True,
            ),
        ]

        self.processor.parser.read_clippings.return_value = clippings
        self.processor.parser.filter_by_book.return_value = clippings

        processed = self.processor.process_clippings("Book A")

        self.assertEqual(len(processed), 1)
        self.assertEqual(processed[0].highlight_text, "Highlight with range")
        self.assertEqual(processed[0].note_text, "Note one before end")
        self.assertEqual(processed[0].categories[0][0], "Category")

    def test_list_books(self):
        """Test listing available books."""
        expected_books = ["Book A", "Book B"]
        self.processor.parser.list_books.return_value = expected_books

        books = self.processor.list_books()

        self.assertEqual(books, expected_books)
        self.processor.parser.list_books.assert_called_once()


if __name__ == "__main__":
    unittest.main()
