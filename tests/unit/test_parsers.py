import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

from src.kindle.models import KindleClipping
from src.kindle.parsers import KindleClippingsParser


class TestKindleClippingsParser(unittest.TestCase):
    def setUp(self):
        """Set up a KindleClippingsParser instance for testing."""
        self.parser = KindleClippingsParser(Path("dummy_path.txt"))

        # Sample clippings for testing (without trailing newlines)
        self.sample_highlight = (
            "Book Title (Author)\n- Your Highlight on page 10 | Location 100-110 | Added on Monday,"
            " February 3, 2025 8:09:12 AM\n\nThis is a highlighted text."
        )

        self.sample_note = (
            "Book Title (Author)\n"
            "- Your Note on page 10 | Location 110 | Added on Monday, February 3, 2025 8:10:00 AM\n"
            "\n"
            "(Category) This is a note."
        )

        self.sample_bookmark = (
            "Book Title (Author)\n- Your Bookmark on page 15 | Location 150 | Added on Monday,"
            " February 3, 2025 9:00:00 AM\n\n"
        )

        self.sample_file_content = (
            f"{self.sample_highlight}\n==========\n"
            f"{self.sample_note}\n==========\n"
            f"{self.sample_bookmark}\n==========\n"
        )

    @patch("builtins.open", new_callable=mock_open)
    def test_read_clippings(self, mock_file):
        """Test reading clippings from a file."""
        mock_file.return_value.read.return_value = self.sample_file_content

        clippings = self.parser.read_clippings()

        self.assertEqual(len(clippings), 3)

        # Compare without worrying about trailing newlines
        self.assertEqual(clippings[0].strip(), self.sample_highlight.strip())
        self.assertEqual(clippings[1].strip(), self.sample_note.strip())
        self.assertEqual(clippings[2].strip(), self.sample_bookmark.strip())

    def test_parse_location(self):
        """Test parsing location strings."""
        self.assertEqual(self.parser.parse_location("100-110"), (100, 110))
        self.assertEqual(self.parser.parse_location("100"), (100, 100))
        self.assertEqual(self.parser.parse_location(""), (0, 0))

    def test_parse_clippings(self):
        """Test parsing raw clippings into structured objects."""
        raw_clippings = [self.sample_highlight, self.sample_note]

        parsed_clippings = self.parser.parse_clippings(raw_clippings)

        self.assertEqual(len(parsed_clippings), 2)

        # Check highlight
        highlight = parsed_clippings[0]
        self.assertIsInstance(highlight, KindleClipping)
        self.assertEqual(highlight.book_title, "Book Title (Author)")
        self.assertEqual(highlight.content, "This is a highlighted text.")
        self.assertEqual(highlight.location, (100, 110))
        self.assertEqual(highlight.location_text, "100-110")
        self.assertTrue(highlight.is_highlight)
        self.assertFalse(highlight.is_note)
        self.assertEqual(highlight.page, "10")

        # Check note
        note = parsed_clippings[1]
        self.assertIsInstance(note, KindleClipping)
        self.assertEqual(note.book_title, "Book Title (Author)")
        self.assertEqual(note.content, "(Category) This is a note.")
        self.assertEqual(note.location, (110, 110))
        self.assertEqual(note.location_text, "110")
        self.assertFalse(note.is_highlight)
        self.assertTrue(note.is_note)
        self.assertEqual(note.page, "10")

    def test_filter_by_book(self):
        """Test filtering clippings by book title."""
        clippings = [
            KindleClipping(
                book_title="Book A",
                content="Content A",
                location=(100, 110),
                location_text="100-110",
                is_highlight=True,
                is_note=False,
            ),
            KindleClipping(
                book_title="Book B",
                content="Content B",
                location=(200, 210),
                location_text="200-210",
                is_highlight=True,
                is_note=False,
            ),
            KindleClipping(
                book_title="Book A",
                content="Content C",
                location=(300, 310),
                location_text="300-310",
                is_highlight=True,
                is_note=False,
            ),
        ]

        filtered = self.parser.filter_by_book(clippings, "Book A")

        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].content, "Content A")
        self.assertEqual(filtered[1].content, "Content C")

    def test_list_books(self):
        """Test listing unique book titles."""
        clippings = [
            KindleClipping(
                book_title="Book B",
                content="Content B",
                location=(200, 210),
                location_text="200-210",
                is_highlight=True,
                is_note=False,
            ),
            KindleClipping(
                book_title="Book A",
                content="Content A",
                location=(100, 110),
                location_text="100-110",
                is_highlight=True,
                is_note=False,
            ),
            KindleClipping(
                book_title="Book A",
                content="Content C",
                location=(300, 310),
                location_text="300-310",
                is_highlight=True,
                is_note=False,
            ),
        ]

        books = self.parser.list_books(clippings)

        self.assertEqual(len(books), 2)
        self.assertEqual(books, ["Book A", "Book B"])  # Should be sorted


if __name__ == "__main__":
    unittest.main()
