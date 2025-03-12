import unittest
from datetime import datetime

from src.kindle.models import KindleClipping, ProcessedHighlight


class TestKindleClipping(unittest.TestCase):
    def test_kindle_clipping_initialization(self):
        """Test initializing a KindleClipping object."""
        # Valid highlight
        highlight = KindleClipping(
            book_title="Book Title",
            content="Highlight content",
            location=(100, 110),
            location_text="100-110",
            added_date=datetime(2025, 2, 3, 8, 0, 0),
            is_highlight=True,
            is_note=False,
            page="10",
        )

        self.assertEqual(highlight.book_title, "Book Title")
        self.assertEqual(highlight.content, "Highlight content")
        self.assertEqual(highlight.location, (100, 110))
        self.assertEqual(highlight.location_text, "100-110")
        self.assertEqual(highlight.added_date, datetime(2025, 2, 3, 8, 0, 0))
        self.assertTrue(highlight.is_highlight)
        self.assertFalse(highlight.is_note)
        self.assertEqual(highlight.page, "10")

        # Valid note
        note = KindleClipping(
            book_title="Book Title",
            content="Note content",
            location=(110, 110),
            location_text="110",
            is_highlight=False,
            is_note=True,
        )

        self.assertEqual(note.book_title, "Book Title")
        self.assertEqual(note.content, "Note content")
        self.assertEqual(note.location, (110, 110))
        self.assertEqual(note.location_text, "110")
        self.assertFalse(note.is_highlight)
        self.assertTrue(note.is_note)
        self.assertIsNone(note.page)

    def test_kindle_clipping_validation(self):
        """Test validation during KindleClipping initialization."""
        # Should raise ValueError if neither highlight nor note
        with self.assertRaises(ValueError):
            KindleClipping(
                book_title="Book Title",
                content="Content",
                location=(100, 110),
                location_text="100-110",
                is_highlight=False,
                is_note=False,
            )


class TestProcessedHighlight(unittest.TestCase):
    def test_processed_highlight_initialization(self):
        """Test initializing a ProcessedHighlight object."""
        highlight = ProcessedHighlight(
            book_name="Book Title",
            location=(100, 110),
            location_text="100-110",
            highlight_text="Highlight content",
            note_text="Note content",
            categories=[["Category", "Subcategory"]],
        )

        self.assertEqual(highlight.book_name, "Book Title")
        self.assertEqual(highlight.location, (100, 110))
        self.assertEqual(highlight.location_text, "100-110")
        self.assertEqual(highlight.highlight_text, "Highlight content")
        self.assertEqual(highlight.note_text, "Note content")
        self.assertEqual(highlight.categories, [["Category", "Subcategory"]])

    def test_processed_highlight_defaults(self):
        """Test default values for ProcessedHighlight."""
        highlight = ProcessedHighlight(
            book_name="Book Title",
            location=(100, 110),
            location_text="100-110",
            highlight_text="Highlight content",
        )

        self.assertEqual(highlight.note_text, "")
        self.assertEqual(highlight.categories, [["No Category"]])


if __name__ == "__main__":
    unittest.main()
