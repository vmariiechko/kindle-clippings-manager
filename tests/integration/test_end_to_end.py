import os
import tempfile
import unittest
from pathlib import Path

from src.kindle.exporters import BulletExporter, MarkdownExporter
from src.kindle.processor import KindleClippingsProcessor


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        """Set up test data for end-to-end testing."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create a sample My Clippings.txt file
        self.clippings_content = """Book Title (Author)
- Your Highlight on page 10 | Location 100-110 | Added on Monday, February 3, 2025 8:09:12 AM

This is a highlighted text.
==========
Book Title (Author)
- Your Note on page 10 | Location 110 | Added on Monday, February 3, 2025 8:10:00 AM

(Category) This is a note.
==========
Book Title (Author)
- Your Highlight on page 20 | Location 200-210 | Added on Monday, February 3, 2025 9:00:00 AM

This is another highlighted text.
==========
Book Title (Author)
- Your Note on page 20 | Location 209 | Added on Monday, February 3, 2025 9:01:00 AM

(Category>Subcategory) This is another note.
==========
Different Book (Another Author)
- Your Highlight on page 30 | Location 300-310 | Added on Tuesday, February 4, 2025 8:00:00 AM

This is a highlight from a different book.
==========
"""

        self.clippings_path = Path(self.temp_dir.name) / "My Clippings.txt"
        with open(self.clippings_path, "w", encoding="utf-8") as f:
            f.write(self.clippings_content)

        # Paths for output files
        self.markdown_path = Path(self.temp_dir.name) / "Categorized Notes.md"
        self.bullet_path = Path(self.temp_dir.name) / "Bullet Notes.txt"

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_process_and_export_markdown(self):
        """Test processing clippings and exporting to markdown."""
        # Process clippings
        processor = KindleClippingsProcessor(self.clippings_path)
        processed_highlights = processor.process_clippings("Book Title (Author)")

        # Export to markdown
        exporter = MarkdownExporter(processed_highlights, self.markdown_path)
        exporter.export()

        # Check that the markdown file was created
        self.assertTrue(self.markdown_path.exists())

        # Read the markdown content
        with open(self.markdown_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Check that categories are properly formatted
        self.assertIn("# Category", markdown_content)
        self.assertIn("## Subcategory", markdown_content)

        # Check that highlights and notes are included
        self.assertIn("This is a highlighted text", markdown_content)
        self.assertIn("This is a note", markdown_content)
        self.assertIn("This is another highlighted text", markdown_content)
        self.assertIn("This is another note", markdown_content)

        # Check that content from the other book is not included
        self.assertNotIn("This is a highlight from a different book", markdown_content)

    def test_process_and_export_bullet(self):
        """Test processing clippings and exporting to bullet format."""
        # Process clippings
        processor = KindleClippingsProcessor(self.clippings_path)
        processed_highlights = processor.process_clippings("Book Title (Author)")

        # Export to bullet format
        exporter = BulletExporter(processed_highlights, self.bullet_path)
        exporter.export()

        # Check that the bullet file was created
        self.assertTrue(self.bullet_path.exists())

        # Read the bullet content
        with open(self.bullet_path, "r", encoding="utf-8") as f:
            bullet_content = f.read()

        # Check that book title is included
        self.assertIn("Book Title (Author)", bullet_content)

        # Check that highlights and notes are included
        self.assertIn("* This is a highlighted text", bullet_content)
        self.assertIn("Note: This is a note", bullet_content)
        self.assertIn("* This is another highlighted text", bullet_content)
        self.assertIn("Note: This is another note", bullet_content)

        # Check that content from the other book is not included
        self.assertNotIn("This is a highlight from a different book", bullet_content)


if __name__ == "__main__":
    unittest.main()
