import unittest

from src.utils.text_utils import CategoryExtractor


class TestCategoryExtractor(unittest.TestCase):
    def test_extract_categories_simple(self):
        """Test extracting a simple category."""
        note = "(Category) This is a note"
        categories = CategoryExtractor.extract_categories(note)

        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0], ["Category"])

    def test_extract_categories_hierarchical(self):
        """Test extracting hierarchical categories."""
        note = "(Category>Subcategory) This is a note"
        categories = CategoryExtractor.extract_categories(note)

        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0], ["Category", "Subcategory"])

    def test_extract_categories_multiple(self):
        """Test extracting multiple categories."""
        note = "(Category1) (Category2) This is a note"
        categories = CategoryExtractor.extract_categories(note)

        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0], ["Category1"])
        self.assertEqual(categories[1], ["Category2"])

    def test_extract_categories_with_mapping(self):
        """Test extracting categories with shortcut mapping."""
        note = "(P) This is a protein note"
        categories = CategoryExtractor.extract_categories(note)

        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0], ["Protein"])

    def test_extract_categories_hierarchical_with_mapping(self):
        """Test extracting hierarchical categories with mapping."""
        note = "(P>FIB) This is a note about protein fiber"
        categories = CategoryExtractor.extract_categories(note)

        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0], ["Protein", "Fiber"])

    def test_extract_categories_no_category(self):
        """Test extracting categories when none are present."""
        note = "This is a note without categories"
        categories = CategoryExtractor.extract_categories(note)

        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0], ["No Category"])

    def test_extract_categories_empty_note(self):
        """Test extracting categories from an empty note."""
        note = ""
        categories = CategoryExtractor.extract_categories(note)

        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0], ["No Category"])

    def test_extract_categories_none_note(self):
        """Test extracting categories from a None note."""
        note = None
        categories = CategoryExtractor.extract_categories(note)

        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0], ["No Category"])

    def test_strip_categories_from_note(self):
        """Test stripping category markers from a note."""
        note = "(Category) This is a note"
        stripped = CategoryExtractor.strip_categories_from_note(note)

        self.assertEqual(stripped, "This is a note")

    def test_strip_multiple_categories_from_note(self):
        """Test stripping multiple category markers from a note."""
        note = "(Category1) (Category2) This is a note"
        stripped = CategoryExtractor.strip_categories_from_note(note)

        self.assertEqual(stripped, "This is a note")

    def test_strip_hierarchical_categories_from_note(self):
        """Test stripping hierarchical category markers from a note."""
        note = "(Category>Subcategory) This is a note"
        stripped = CategoryExtractor.strip_categories_from_note(note)

        self.assertEqual(stripped, "This is a note")

    def test_strip_categories_no_category(self):
        """Test stripping categories when none are present."""
        note = "This is a note without categories"
        stripped = CategoryExtractor.strip_categories_from_note(note)

        self.assertEqual(stripped, "This is a note without categories")

    def test_strip_categories_empty_note(self):
        """Test stripping categories from an empty note."""
        note = ""
        stripped = CategoryExtractor.strip_categories_from_note(note)

        self.assertEqual(stripped, "")

    def test_strip_categories_none_note(self):
        """Test stripping categories from a None note."""
        note = None
        stripped = CategoryExtractor.strip_categories_from_note(note)

        self.assertEqual(stripped, "")


if __name__ == "__main__":
    unittest.main()
