import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from src.kindle.exporters import BulletExporter, DefaultExporter, MarkdownExporter
from src.kindle.models import ProcessedHighlight


class TestMarkdownExporter(unittest.TestCase):
    def setUp(self):
        """Set up test data for exporters."""
        self.highlights = [
            ProcessedHighlight(
                book_name="Book A",
                location=(100, 110),
                location_text="100-110",
                highlight_text="Highlight 1",
                note_text="Note 1",
                categories=[["Category1"]],
            ),
            ProcessedHighlight(
                book_name="Book A",
                location=(200, 210),
                location_text="200-210",
                highlight_text="Highlight 2",
                note_text="Note 2",
                categories=[["Category1", "Subcategory"]],
            ),
            ProcessedHighlight(
                book_name="Book A",
                location=(300, 310),
                location_text="300-310",
                highlight_text="Highlight 3",
                note_text="",
                categories=[["Category2"]],
            ),
            ProcessedHighlight(
                book_name="Book A",
                location=(400, 410),
                location_text="400-410",
                highlight_text="Highlight with case issue",
                note_text="Note with case issue",
                categories=[["category1"]],  # Lowercase version of Category1
            ),
            ProcessedHighlight(
                book_name="Book A",
                location=(500, 510),
                location_text="500-510",
                highlight_text="Highlight with spacing issue",
                note_text="Note with spacing issue",
                categories=[["Я- мужчина"]],  # Spacing issue
            ),
        ]

        self.output_path = Path("test_output.md")

    def test_normalize_category(self):
        """Test category normalization."""
        exporter = MarkdownExporter(self.highlights, self.output_path)

        # Test case normalization
        self.assertEqual(exporter._normalize_category("Category1"), "category1")
        self.assertEqual(exporter._normalize_category("CATEGORY1"), "category1")

        # Test spacing normalization
        self.assertEqual(exporter._normalize_category("Я- мужчина"), "я-мужчина")
        self.assertEqual(exporter._normalize_category("Я - мужчина"), "я-мужчина")

    def test_format_category_display(self):
        """Test category display formatting."""
        exporter = MarkdownExporter(self.highlights, self.output_path)

        # Test title case
        self.assertEqual(exporter._format_category_display("category1"), "Category1")

        # Test spacing formatting
        self.assertEqual(exporter._format_category_display("Я- мужчина"), "Я - Мужчина")
        self.assertEqual(exporter._format_category_display("Я -мужчина"), "Я - Мужчина")

    @patch("builtins.open", new_callable=mock_open)
    def test_export_markdown(self, mock_file):
        """Test exporting highlights to markdown."""
        exporter = MarkdownExporter(self.highlights, self.output_path)
        exporter.export()

        # Check that the file was opened for writing
        mock_file.assert_called_once_with(self.output_path, "w", encoding="utf-8")

        # Get the written content
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)

        # Check that categories are properly formatted
        self.assertIn("# Category1", written_content)
        self.assertIn("## Subcategory", written_content)
        self.assertIn("# Category2", written_content)

        # Check that highlights and notes are included
        self.assertIn("* Highlight 1", written_content)
        self.assertIn("**Note**: *Note 1*", written_content)
        self.assertIn("* Highlight 2", written_content)
        self.assertIn("**Note**: *Note 2*", written_content)
        self.assertIn("* Highlight 3", written_content)

        # Check that case-insensitive categories are merged
        self.assertNotIn("# category1", written_content)  # Lowercase version should not appear

        # Check that spacing issues are fixed
        self.assertIn("# Я - Мужчина", written_content)


class TestBulletExporter(unittest.TestCase):
    def setUp(self):
        """Set up test data for exporters."""
        self.highlights = [
            ProcessedHighlight(
                book_name="Book A",
                location=(100, 110),
                location_text="100-110",
                highlight_text="Highlight 1",
                note_text="Note 1",
                categories=[["Category1"]],
            ),
            ProcessedHighlight(
                book_name="Book A",
                location=(200, 210),
                location_text="200-210",
                highlight_text="Highlight 2",
                note_text="",
                categories=[["Category1", "Subcategory"]],
            ),
            ProcessedHighlight(
                book_name="Book B",
                location=(300, 310),
                location_text="300-310",
                highlight_text="Highlight 3",
                note_text="Note 3",
                categories=[["Category2"]],
            ),
        ]

        self.output_path = Path("test_output.txt")

    @patch("builtins.open", new_callable=mock_open)
    def test_export_bullet(self, mock_file):
        """Test exporting highlights to bullet format."""
        exporter = BulletExporter(self.highlights, self.output_path)
        exporter.export()

        # Check that the file was opened for writing
        mock_file.assert_called_once_with(self.output_path, "w", encoding="utf-8")

        # Get the written content
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)

        # Check that book titles are included
        self.assertIn("=========== Book A ===========", written_content)
        self.assertIn("=========== Book B ===========", written_content)

        # Check that highlights and notes are included
        self.assertIn("* Highlight 1", written_content)
        self.assertIn("  - Note: Note 1", written_content)
        self.assertIn("* Highlight 2", written_content)
        self.assertIn("* Highlight 3", written_content)
        self.assertIn("  - Note: Note 3", written_content)


class TestDefaultExporter(unittest.TestCase):
    def setUp(self):
        """Set up test data for exporters."""
        self.raw_clippings = [
            "Book A (Author)\n- Your Highlight on Location 100-110 | Added on Date\n\nHighlight 1",
            "Book A (Author)\n- Your Note on Location 110 | Added on Date\n\nNote 1",
            "Book B (Author)\n- Your Highlight on Location 200-210 | Added on Date\n\nHighlight 2",
        ]

        self.output_path = Path("test_output.txt")

    @patch("builtins.open", new_callable=mock_open)
    def test_export_default(self, mock_file):
        """Test exporting clippings to default format."""
        exporter = DefaultExporter(self.raw_clippings, self.output_path)
        exporter.export()

        # Check that the file was opened for writing
        mock_file.assert_called_once_with(self.output_path, "w", encoding="utf-8")

        # Get the written content
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)

        # Check that all clippings are included
        self.assertIn("Book A (Author)", written_content)
        self.assertIn("Highlight 1", written_content)
        self.assertIn("Note 1", written_content)
        self.assertIn("Book B (Author)", written_content)
        self.assertIn("Highlight 2", written_content)

        # Check that delimiters are added
        self.assertIn("==========", written_content)


if __name__ == "__main__":
    unittest.main()
